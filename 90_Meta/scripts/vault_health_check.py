#!/usr/bin/env /usr/bin/python3
"""
vault_health_check.py
vault 全体の品質をチェックし、90_Meta/health-reports/ にレポート出力する。

チェック項目:
  - CRITICAL: review_due 超過 / 必須フィールド欠損 / 実名混入疑い
  - WARNING: review_due 近接 / 壊れ wikilink / 孤児ノート / weight 範囲外
  - INFO: 成長指標 / relations 密度 / type 使用実績
"""

import re
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import Counter, defaultdict

try:
    import frontmatter
except ImportError:
    print("pip install python-frontmatter が必要")
    exit(1)

VAULT = Path(__file__).resolve().parents[2]
REPORT_DIR = VAULT / "90_Meta" / "health-reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDE_DIRS = {".obsidian", ".claude", ".github", "raw", "90_Meta/templates", "90_Meta/health-reports", "90_Meta/amendment-reports", "90_Meta/scripts", "docs", "mcp_server"}
EXCLUDE_FILES = {"90_Meta/alias_map.md", "CONTRIBUTING.md", "README.md"}

# 層別必須フィールド
REQUIRED_FIELDS = {
    "law":        ["source_url", "version", "effective_date", "review_due", "issuer"],
    "guideline":  ["issuer", "source_url", "version", "effective_date", "review_due"],
    "service":    ["law_basis", "target", "version", "review_due"],
    "framework":  ["origin", "year", "domain"],
    "disorder":   [],  # icd11_code OR dsm5_code の片方あればOK
    "method":     ["evidence_level", "target_disorder"],
    "assessment": ["administrator", "time_required", "purpose"],
    "org":        ["role", "mandate"],
    "person":     ["id", "status", "diagnosis"],
}

# リンク型辞書
VALID_REL_TYPES = {
    "applies-to", "compliance-required", "mandatory-report-trigger",
    "eligible-service", "currently-using", "considered", "discontinued",
    "has-characteristic", "responds-to", "contraindicated", "recommended",
    "evidence-based", "underpinned-by", "comorbid-with", "provided-by",
    "mandated-by", "escalate-to", "complements", "contradicts", "supersedes",
    "derived-from", "supersedes-at", "delivers", "informs", "instance-of",
    "explains", "referred-by", "supports", "supersedes-at",
}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]")
REALNAME_COMMENT = "<!-- allow-realname -->"


def load_fm_safely(md_path: Path):
    """HTMLコメント <!-- allow-realname --> を除去してから frontmatter.loads"""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    # 先頭コメント除去
    clean_lines = lines[:]
    while clean_lines and (clean_lines[0].strip().startswith("<!--") or clean_lines[0].strip() == ""):
        clean_lines.pop(0)
    cleaned = "\n".join(clean_lines)
    try:
        post = frontmatter.loads(cleaned)
    except Exception as e:
        return None, content, str(e)
    return post, content, None


def iter_vault_mds():
    for md in VAULT.rglob("*.md"):
        rel = md.relative_to(VAULT)
        parts = rel.parts
        if any(str(rel).startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        if str(rel) in EXCLUDE_FILES:
            continue
        if parts[0] in {".obsidian", ".claude", ".github", "docs", "mcp_server"}:
            continue
        if "raw" in parts or "templates" in parts or "health-reports" in parts or "amendment-reports" in parts:
            continue
        yield md


def md_to_id(md: Path) -> str:
    rel = md.relative_to(VAULT)
    return str(rel.with_suffix(""))


def extract_wikilink_target(link: str) -> str:
    s = link.strip()
    if s.startswith("[[") and s.endswith("]]"):
        s = s[2:-2]
    if "|" in s:
        s = s.split("|", 1)[0]
    return s.strip()


def today():
    return date.today()


def parse_date(v):
    if isinstance(v, (date, datetime)):
        return v if isinstance(v, date) else v.date()
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def check_vault():
    mds = list(iter_vault_mds())
    all_ids = {md_to_id(md) for md in mds}
    ids_by_name = defaultdict(list)  # stem → [full_id, ...]
    for md in mds:
        ids_by_name[md.stem].append(md_to_id(md))

    critical = {"expired": [], "missing_required": [], "realname_suspect": [], "parse_error": []}
    warning = {"due_soon": [], "broken_link": [], "orphan": [], "weight_oor": [], "type_unknown": []}
    info = {"layer_counts": Counter(), "type_counts": Counter(), "rel_type_counts": Counter(),
            "rel_density": [], "total_mds": 0, "total_with_fm": 0, "total_relations": 0}

    referenced = set()  # 被参照されたid

    # Pass 1: ノード収集 + 各チェック
    for md in mds:
        rel_path = str(md.relative_to(VAULT))
        post, content, err = load_fm_safely(md)
        info["total_mds"] += 1

        # 層別カウント
        layer = rel_path.split("/", 1)[0]
        info["layer_counts"][layer] += 1

        # パースエラー
        if post is None:
            critical["parse_error"].append((rel_path, err))
            continue

        if not post.metadata:
            # frontmatter なし
            continue

        info["total_with_fm"] += 1
        meta = post.metadata
        node_type = meta.get("type", "")
        node_status = meta.get("status", "active")
        is_archived = node_status == "archived" or "archived" in Path(rel_path).parts
        info["type_counts"][node_type] += 1

        # 必須フィールドチェック（archived ノードは review_due 等を除外）
        if node_type in REQUIRED_FIELDS:
            missing = []
            for f in REQUIRED_FIELDS[node_type]:
                # archived ノードは review_due / monitoring_url 系を要求しない
                if is_archived and f in ("review_due", "monitoring_url"):
                    continue
                v = meta.get(f, None)
                if v is None or v == "" or v == []:
                    missing.append(f)
            # disorder の特例: icd11 OR dsm5
            if node_type == "disorder":
                if not meta.get("icd11_code") and not meta.get("dsm5_code"):
                    missing.append("icd11_code or dsm5_code")
            if missing:
                critical["missing_required"].append((rel_path, node_type, missing))

        # review_due チェック
        rd = parse_date(meta.get("review_due"))
        if rd:
            today_d = today()
            if rd < today_d:
                critical["expired"].append((rel_path, rd, (today_d - rd).days))
            elif (rd - today_d).days <= 30:
                warning["due_soon"].append((rel_path, rd, (rd - today_d).days))

        # realname 疑い（簡易）: 漢字+スペース+漢字パターン。ただし allow-realname マーカーありは除外
        if REALNAME_COMMENT not in content:
            # 本文のみチェック（frontmatter 除外）
            body = post.content
            # 簡易日本人名パターン（苗字漢字2-4 + 空白 + 名前漢字2-4）
            name_pattern = re.compile(r"[一-龥]{2,4}\s+[一-龥]{2,4}")
            for m in name_pattern.finditer(body):
                # 記号を含むコンテキストは誤検出しやすいのでスキップ判定
                token = m.group()
                if any(c.isdigit() for c in token):
                    continue
                critical["realname_suspect"].append((rel_path, "[検出あり・箇所明示は記録しない]"))
                break

        # relations チェック
        relations = meta.get("relations") or []
        if not isinstance(relations, list):
            continue

        info["total_relations"] += len(relations)
        info["rel_density"].append((rel_path, len(relations)))

        for rel_idx, r in enumerate(relations):
            if not isinstance(r, dict):
                continue
            rtype = r.get("type", "")
            info["rel_type_counts"][rtype] += 1

            # type 辞書チェック
            if rtype and rtype not in VALID_REL_TYPES:
                warning["type_unknown"].append((rel_path, rel_idx, rtype))

            # weight 範囲
            w = r.get("weight")
            if w is not None:
                try:
                    wf = float(w)
                    if wf < 0 or wf > 1:
                        warning["weight_oor"].append((rel_path, rel_idx, wf))
                except (ValueError, TypeError):
                    warning["weight_oor"].append((rel_path, rel_idx, str(w)))

            # 壊れリンクチェック
            target_link = r.get("to", "")
            target = extract_wikilink_target(target_link)
            if not target:
                continue
            # 完全一致 or suffix 一致
            if target in all_ids:
                referenced.add(target)
            else:
                candidates = [i for i in all_ids if i.endswith("/" + target) or i == target]
                if candidates:
                    referenced.add(candidates[0])
                else:
                    warning["broken_link"].append((rel_path, target))

        # 本文 wikilink も被参照マーク（孤児ノート判定用）
        for m in WIKILINK_RE.finditer(post.content):
            target = extract_wikilink_target("[[" + m.group(1) + "]]")
            if target in all_ids:
                referenced.add(target)
            else:
                candidates = [i for i in all_ids if i.endswith("/" + target) or i == target]
                if candidates:
                    referenced.add(candidates[0])

    # 孤児ノート判定
    # 除外: README.md, MOC, meta, layer-readme, archived/ 類
    for md in mds:
        rel_path = str(md.relative_to(VAULT))
        if md.stem == "README":
            continue
        if md.stem == "SCHEMA":
            continue
        if "MOC" in rel_path or "Knowledge.md" in rel_path or "Sexuality.md" in rel_path:
            continue
        # archived/ 配下は意図的に現行ノートから直接リンクされない場合がある
        if "archived" in Path(rel_path).parts:
            continue

        post, _, err = load_fm_safely(md)
        if err or not post or not post.metadata:
            continue

        node_type = post.metadata.get("type", "")
        if node_type in {"moc", "layer-readme", "meta"}:
            continue

        # status: archived も除外
        if post.metadata.get("status") == "archived":
            continue

        nid = md_to_id(md)
        if nid in referenced:
            continue

        # relations もなく、被参照もない
        relations = post.metadata.get("relations") or []
        if not relations:
            warning["orphan"].append(rel_path)

    return critical, warning, info


def generate_report(critical, warning, info):
    today_d = today()
    report_lines = []
    R = report_lines.append

    R(f"---")
    R(f"type: meta")
    R(f"tags: [meta, health-report]")
    R(f"cssclasses: [layer-meta]")
    R(f"generated_at: {today_d.isoformat()}")
    R(f"---")
    R(f"")
    R(f"<!-- allow-realname -->")
    R(f"")
    R(f"# vault health-check レポート")
    R(f"")
    R(f"**実行日**: {today_d.isoformat()}")
    R(f"**対象ファイル数**: {info['total_mds']}")
    R(f"**frontmatter あり**: {info['total_with_fm']}")
    R(f"**relations 総数**: {info['total_relations']}")
    R(f"")

    # サマリ
    critical_total = sum(len(v) for v in critical.values())
    warning_total = sum(len(v) for v in warning.values())
    R(f"## 🚨 サマリ")
    R(f"")
    R(f"| 重大度 | 件数 |")
    R(f"|---|---|")
    R(f"| 🔴 CRITICAL | {critical_total} |")
    R(f"| 🟡 WARNING | {warning_total} |")
    R(f"")

    # CRITICAL
    R(f"## 🔴 CRITICAL")
    R(f"")

    R(f"### 1. review_due 超過 ({len(critical['expired'])}件)")
    if critical["expired"]:
        for path, d, days in critical["expired"]:
            R(f"- `{path}`: {d} (超過 {days}日)")
    else:
        R(f"なし")
    R(f"")

    R(f"### 2. 必須フィールド欠損 ({len(critical['missing_required'])}件)")
    if critical["missing_required"]:
        for path, t, miss in critical["missing_required"]:
            R(f"- `{path}` (type: {t}): {', '.join(miss)}")
    else:
        R(f"なし")
    R(f"")

    R(f"### 3. 実名混入の疑い ({len(critical['realname_suspect'])}件)")
    if critical["realname_suspect"]:
        for path, _ in critical["realname_suspect"]:
            R(f"- `{path}` ← `<!-- allow-realname -->` マーカーがなく漢字ペアが検出された。内容確認を推奨。")
    else:
        R(f"なし")
    R(f"")

    R(f"### 4. パースエラー ({len(critical['parse_error'])}件)")
    if critical["parse_error"]:
        for path, err in critical["parse_error"]:
            R(f"- `{path}`: {err}")
    else:
        R(f"なし")
    R(f"")

    # WARNING
    R(f"## 🟡 WARNING")
    R(f"")

    R(f"### 5. review_due 近接（30日以内）({len(warning['due_soon'])}件)")
    if warning["due_soon"]:
        for path, d, days in warning["due_soon"]:
            R(f"- `{path}`: {d} (残り {days}日)")
    else:
        R(f"なし")
    R(f"")

    R(f"### 6. 壊れた wikilink ({len(warning['broken_link'])}件)")
    if warning["broken_link"]:
        # ソース別にグルーピング
        by_source = defaultdict(list)
        for src, target in warning["broken_link"]:
            by_source[src].append(target)
        for src, targets in by_source.items():
            R(f"- `{src}` → 未解決:")
            for t in targets:
                R(f"  - `{t}`")
    else:
        R(f"なし")
    R(f"")

    R(f"### 7. 孤児ノート ({len(warning['orphan'])}件)")
    if warning["orphan"]:
        for path in warning["orphan"]:
            R(f"- `{path}`")
    else:
        R(f"なし")
    R(f"")

    R(f"### 8. relations weight 範囲外 ({len(warning['weight_oor'])}件)")
    if warning["weight_oor"]:
        for src, idx, w in warning["weight_oor"]:
            R(f"- `{src}` relations[{idx}]: weight = {w}")
    else:
        R(f"なし")
    R(f"")

    R(f"### 9. type 辞書外使用 ({len(warning['type_unknown'])}件)")
    if warning["type_unknown"]:
        for src, idx, t in warning["type_unknown"]:
            R(f"- `{src}` relations[{idx}]: type = `{t}`")
    else:
        R(f"なし")
    R(f"")

    # INFO
    R(f"## 🟢 INFO")
    R(f"")

    R(f"### 10. 層別ページ数")
    R(f"")
    R(f"| 層 | ページ数 |")
    R(f"|---|---|")
    for layer, c in sorted(info["layer_counts"].items()):
        R(f"| {layer} | {c} |")
    R(f"")

    R(f"### 11. type 別ページ数")
    R(f"")
    R(f"| type | 数 |")
    R(f"|---|---|")
    for t, c in info["type_counts"].most_common():
        R(f"| {t} | {c} |")
    R(f"")

    R(f"### 12. relations type 使用実績")
    R(f"")
    R(f"| type | 数 |")
    R(f"|---|---|")
    for t, c in info["rel_type_counts"].most_common():
        R(f"| {t} | {c} |")
    R(f"")

    R(f"### 13. relations 密度（上位10）")
    R(f"")
    R(f"| ノート | relations数 |")
    R(f"|---|---|")
    rel_density_sorted = sorted(info["rel_density"], key=lambda x: -x[1])[:10]
    for path, n in rel_density_sorted:
        R(f"| `{path}` | {n} |")
    R(f"")

    avg_rels = info["total_relations"] / max(info["total_with_fm"], 1)
    R(f"**全体平均**: {avg_rels:.1f} relations/ノート（frontmatter あり {info['total_with_fm']}件に対し）")
    R(f"")

    # アクション
    R(f"## 🎯 推奨アクション")
    R(f"")
    R(f"### 最優先（今週中）")
    if critical_total > 0:
        if critical["expired"]:
            R(f"- [ ] review_due 超過 {len(critical['expired'])}件 の期限更新")
        if critical["missing_required"]:
            R(f"- [ ] 必須フィールド欠損 {len(critical['missing_required'])}件 の補完")
        if critical["realname_suspect"]:
            R(f"- [ ] 実名混入疑い {len(critical['realname_suspect'])}件 の内容確認・仮名化")
        if critical["parse_error"]:
            R(f"- [ ] パースエラー {len(critical['parse_error'])}件 の修正")
    else:
        R(f"- CRITICAL 項目なし")
    R(f"")

    R(f"### 計画的（今月中）")
    if warning_total > 0:
        if warning["broken_link"]:
            R(f"- [ ] 壊れ wikilink {len(warning['broken_link'])}件 の stub 作成 or 修正")
        if warning["orphan"]:
            R(f"- [ ] 孤児ノート {len(warning['orphan'])}件 の relations 追加 or 削除")
        if warning["due_soon"]:
            R(f"- [ ] 期限近接 {len(warning['due_soon'])}件 の事前確認")
        if warning["type_unknown"]:
            R(f"- [ ] 辞書外 type {len(warning['type_unknown'])}件 の辞書追加 or 修正")
        if warning["weight_oor"]:
            R(f"- [ ] weight 範囲外 {len(warning['weight_oor'])}件 の修正")
    else:
        R(f"- WARNING 項目なし")
    R(f"")

    return "\n".join(report_lines)


def main():
    print(f"vault: {VAULT}")
    print(f"チェック実行中...")

    critical, warning, info = check_vault()
    report = generate_report(critical, warning, info)

    out_path = REPORT_DIR / f"{today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")

    critical_total = sum(len(v) for v in critical.values())
    warning_total = sum(len(v) for v in warning.values())

    print(f"\n✅ レポート生成完了")
    print(f"  出力: {out_path.relative_to(VAULT)}")
    print(f"  CRITICAL: {critical_total}")
    print(f"  WARNING: {warning_total}")
    print(f"  対象ファイル: {info['total_mds']}")
    print(f"  relations 総数: {info['total_relations']}")


if __name__ == "__main__":
    main()
