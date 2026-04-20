#!/usr/bin/env /usr/bin/python3
"""
sync_to_neo4j.py
my-skill-graph vault の frontmatter relations を Neo4j にフル同期する。

使い方:
  python3 90_Meta/scripts/sync_to_neo4j.py

要件:
  pip install neo4j python-frontmatter

前提:
  - Docker で Neo4j コンテナ neo4j-skillgraph が起動中
  - bolt://localhost:7687, auth: neo4j/skillgraph2026
"""

import os
import re
import sys
from pathlib import Path
from datetime import date, datetime

try:
    import frontmatter
    from neo4j import GraphDatabase
except ImportError as e:
    print(f"依存パッケージが不足: {e}")
    print("  pip install neo4j python-frontmatter")
    sys.exit(1)

# .env 読込（任意）
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass  # python-dotenv が無くても環境変数直接指定なら動く

VAULT = Path(__file__).resolve().parents[2]
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

if not NEO4J_PASSWORD:
    print("エラー: 環境変数 NEO4J_PASSWORD が設定されていません")
    print("  以下のいずれかで設定してください:")
    print("  1. export NEO4J_PASSWORD='yourpassword'")
    print("  2. プロジェクトルートに .env ファイルを作成（.env.example 参照）")
    sys.exit(1)

NEO4J_AUTH = (NEO4J_USER, NEO4J_PASSWORD)

# 除外ディレクトリ・ファイル
EXCLUDE_DIRS = {".obsidian", ".claude", "raw", "90_Meta/templates", "90_Meta/health-reports"}
EXCLUDE_FILES = {"90_Meta/alias_map.md"}  # 暗号化済みファイルは同期対象外（セキュリティ）

# type → Neo4j label 変換
TYPE_TO_LABEL = {
    "law": "Law",
    "guideline": "Guideline",
    "framework": "Framework",
    "disorder": "Disorder",
    "method": "Method",
    "assessment": "Assessment",
    "service": "Service",
    "org": "Org",
    "person": "Person",
    "episode": "Episode",
    "insight": "Insight",
    "stakeholder": "Stakeholder",
    "care-role": "CareRole",
    "care_role": "CareRole",     # アンダースコア版も吸収
    "substitute": "Substitute",
    "simulation": "Simulation",
    "moc": "Moc",
    "layer-readme": "LayerReadme",
    "meta": "Meta",
    "alias_map": "Meta",         # alias_map も Meta 扱い
}

# relations.type → Neo4j relationship 変換
REL_TYPE_MAP = {
    "applies-to": "APPLIES_TO",
    "compliance-required": "COMPLIANCE_REQUIRED",
    "mandatory-report-trigger": "MANDATORY_REPORT_TRIGGER",
    "eligible-service": "ELIGIBLE_FOR",
    "currently-using": "USING",
    "considered": "CONSIDERED",
    "discontinued": "DISCONTINUED",
    "has-characteristic": "HAS_CHARACTERISTIC",
    "responds-to": "RESPONDS_TO",
    "contraindicated": "CONTRAINDICATED",
    "recommended": "RECOMMENDED",
    "evidence-based": "EVIDENCE_BASED",
    "underpinned-by": "UNDERPINNED_BY",
    "comorbid-with": "COMORBID_WITH",
    "provided-by": "PROVIDED_BY",
    "mandated-by": "MANDATED_BY",
    "escalate-to": "ESCALATE_TO",
    "complements": "COMPLEMENTS",
    "contradicts": "CONTRADICTS",
    "supersedes": "SUPERSEDES",
    "superseded-by": "SUPERSEDED_BY",
    "amendment-of": "AMENDMENT_OF",
    "pending-amendment": "PENDING_AMENDMENT",
    "derived-from": "DERIVED_FROM",
    "supersedes-at": "SUPERSEDES_AT",
    "delivers": "DELIVERS",
    "informs": "INFORMS",
    "instance-of": "INSTANCE_OF",
    "explains": "EXPLAINS",
    "supports": "SUPPORTS",
    "referred-by": "REFERRED_BY",
}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]")


def load_frontmatter_safely(md_path: Path):
    """HTML コメント <!-- allow-realname --> を先頭から除去してから frontmatter.loads する"""
    content = md_path.read_text(encoding="utf-8")
    # 先頭の HTML コメント行を除去（realname-check hook 用マーカー）
    lines = content.splitlines()
    while lines and (lines[0].strip().startswith("<!--") or lines[0].strip() == ""):
        lines.pop(0)
    cleaned = "\n".join(lines)
    return frontmatter.loads(cleaned)


def iter_vault_mds():
    """vault 内の対象 .md を走査"""
    for md in VAULT.rglob("*.md"):
        rel = md.relative_to(VAULT)
        parts = rel.parts
        # 除外
        if any(str(rel).startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        if str(rel) in EXCLUDE_FILES:
            continue
        if parts[0] in {".obsidian", ".claude"}:
            continue
        if "raw" in parts or "templates" in parts or "health-reports" in parts:
            continue
        # README.md は層の説明として含める
        yield md


def extract_wikilink_target(wikilink: str) -> str:
    """[[path/name]] or [[name]] から target path を抽出"""
    s = wikilink.strip()
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2]
    # エイリアス除去
    if "|" in s:
        s = s.split("|", 1)[0]
    return s.strip()


def md_to_id(md: Path) -> str:
    """ファイルパスを Neo4j ノードID に（拡張子なし・vault相対）"""
    rel = md.relative_to(VAULT)
    return str(rel.with_suffix(""))


def clean_value(v):
    """Neo4j で保存可能な型に変換"""
    if v is None:
        return None
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    if isinstance(v, list):
        return [clean_value(x) for x in v if x is not None]
    if isinstance(v, dict):
        # dict は JSON 文字列化
        import json
        return json.dumps(v, ensure_ascii=False, default=str)
    return v


def create_or_update_node(tx, md: Path, meta: dict):
    """ノードを作成。nid (Neo4j-internal ID) は vault相対パスで固定、
    frontmatter の id は alias_id として別キーで保持（上書き回避）"""
    node_id = md_to_id(md)
    raw_type = meta.get("type", "unknown")
    label = TYPE_TO_LABEL.get(raw_type, "Node")

    props = {
        "name": md.stem,
        "type": raw_type,
    }
    # frontmatter フィールドをマージ（id も含むが後で alias_id に退避）
    for k, v in meta.items():
        if k in ("relations",):
            continue
        if v is None or v == "":
            continue
        cv = clean_value(v)
        if cv is not None:
            props[k] = cv

    # frontmatter の id を alias_id に退避（P-0001 等の短縮ID）
    if "id" in props:
        props["alias_id"] = props.pop("id")

    # 固定 nid（パスベース）と layer を最後に設定（上書き防止）
    props["nid"] = node_id
    props["path"] = str(md.relative_to(VAULT))

    # layer = 第一階層（クエリ容易化のため）
    rel_path = md.relative_to(VAULT)
    parts = rel_path.parts
    if len(parts) >= 2 and parts[1] == "archived":
        # 60_Laws/archived/foo.md → layer = 60_Laws, archived = True
        props["layer"] = parts[0]
        props["archived"] = True
    else:
        props["layer"] = parts[0]
        props["archived"] = False

    # status デフォルト
    if "status" not in props:
        if props.get("archived"):
            props["status"] = "archived"
        else:
            props["status"] = "active"

    tx.run(
        f"MERGE (n {{nid: $nid}}) "
        f"SET n:{label}, n += $props",
        nid=node_id, props=props
    )


def create_relationship(tx, source_md: Path, rel: dict, all_ids: set):
    """関係を作成"""
    source_id = md_to_id(source_md)
    raw_type = rel.get("type", "related-to")
    rel_type = REL_TYPE_MAP.get(raw_type, raw_type.upper().replace("-", "_"))

    target_wikilink = rel.get("to", "")
    target = extract_wikilink_target(target_wikilink)

    # 解決ロジック:
    # 1) 完全一致 (そのまま)
    # 2) suffix一致（例: "障害者総合支援法" → "60_Laws/障害者総合支援法"）
    if target in all_ids:
        resolved = target
    else:
        candidates = [i for i in all_ids if i.endswith("/" + target) or i == target]
        if candidates:
            resolved = candidates[0]
        else:
            return False  # 壊れたリンク

    props = {}
    for k in ("weight", "evidence", "rationale", "source", "condition", "updated"):
        if k in rel and rel[k] not in (None, ""):
            props[k] = clean_value(rel[k])
    # 元の type 文字列も保存
    props["type_raw"] = raw_type

    tx.run(
        f"MATCH (a {{nid: $source}}), (b {{nid: $target}}) "
        f"MERGE (a)-[r:{rel_type}]->(b) "
        f"SET r = $props",
        source=source_id, target=resolved, props=props
    )
    return True


def sync():
    print(f"vault: {VAULT}")
    print(f"Neo4j: {NEO4J_URI}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

    with driver.session() as session:
        # 1. クリア
        print("\n[1/4] Neo4j をクリア...")
        session.run("MATCH (n) DETACH DELETE n")

        # 2. 全ノード収集
        print("[2/4] ノード収集中...")
        mds = list(iter_vault_mds())
        nodes_created = 0
        failed_parse = 0
        all_ids = set()

        for md in mds:
            try:
                post = load_frontmatter_safely(md)
            except Exception as e:
                print(f"  parse失敗: {md.relative_to(VAULT)}: {e}")
                failed_parse += 1
                continue

            if not post.metadata:
                continue

            all_ids.add(md_to_id(md))
            try:
                session.execute_write(create_or_update_node, md, post.metadata)
                nodes_created += 1
            except Exception as e:
                print(f"  node作成失敗: {md.relative_to(VAULT)}: {e}")

        print(f"  ノード作成: {nodes_created} / パース失敗: {failed_parse}")

        # 3. 関係作成
        print("[3/4] 関係作成中...")
        rels_created = 0
        rels_broken = 0
        amendment_rels = 0
        for md in mds:
            try:
                post = load_frontmatter_safely(md)
            except Exception:
                continue

            # 通常の relations
            relations = post.metadata.get("relations", []) or []
            for rel in relations:
                if not isinstance(rel, dict):
                    continue
                try:
                    ok = session.execute_write(create_relationship, md, rel, all_ids)
                    if ok:
                        rels_created += 1
                    else:
                        rels_broken += 1
                        print(f"  未解決リンク: {md.relative_to(VAULT)} → {rel.get('to')}")
                except Exception as e:
                    print(f"  関係作成失敗: {md.relative_to(VAULT)}: {e}")

            # 改正追随: superseded_by / supersedes フィールドから自動関係生成
            for fm_key, rel_type in [("superseded_by", "superseded-by"), ("supersedes", "supersedes")]:
                fm_val = post.metadata.get(fm_key)
                if not fm_val:
                    continue
                synthetic_rel = {
                    "to": fm_val if isinstance(fm_val, str) else str(fm_val),
                    "type": rel_type,
                    "weight": 1.0,
                    "evidence": f"frontmatter.{fm_key}",
                }
                try:
                    ok = session.execute_write(create_relationship, md, synthetic_rel, all_ids)
                    if ok:
                        amendment_rels += 1
                except Exception as e:
                    print(f"  改正追随関係失敗: {md.relative_to(VAULT)}: {e}")

        print(f"  関係作成: {rels_created} / 改正追随: {amendment_rels} / 未解決: {rels_broken}")

        # 4. サマリ
        print("\n[4/4] サマリ取得...")
        result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c ORDER BY c DESC")
        print("\nノード種別別件数:")
        for r in result:
            print(f"  {r['label']}: {r['c']}")

        result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS c ORDER BY c DESC LIMIT 10")
        print("\n関係種別別件数 (Top 10):")
        for r in result:
            print(f"  {r['type']}: {r['c']}")

    driver.close()
    print("\n✅ 同期完了")
    print(f"\nNeo4j Browser: http://localhost:7474")
    print(f"  ユーザー: neo4j / パスワード: skillgraph2026")


if __name__ == "__main__":
    sync()
