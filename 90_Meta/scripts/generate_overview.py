#!/usr/bin/env /usr/bin/python3
"""
generate_overview.py
vault 俯瞰ダッシュボード overview.md を生成する（data-wiki/CLAUDE.md §3 overview モード相当）。

生成内容:
  1. 層別ページ数テーブル
  2. type 別ページ数
  3. 最近の変更（git log 直近 10 件）
  4. 改正追随状況（pending-amendment / expired / due_soon）
  5. 孤児ノート・壊れリンクのサマリ
  6. 関係密度 Top 10（よく参照されるノード）
  7. Mermaid 層間関係グラフ
"""

import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("pip install python-frontmatter が必要")
    exit(1)

VAULT = Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {
    ".obsidian", ".claude", ".github", "raw",
    "90_Meta/templates", "90_Meta/health-reports",
    "90_Meta/amendment-reports", "90_Meta/scripts",
    "docs", "mcp_server",
}
EXCLUDE_FILES = {
    "90_Meta/alias_map.md",
    "README.md",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "log.md",
    "overview.md",
}

LAYER_ORDER = [
    "00_MOC", "10_People", "20_Episodes", "30_Insights",
    "40_Stakeholders", "50_Resilience",
    "60_Laws", "61_Guidelines", "62_Frameworks",
    "63_Disorders", "64_Methods", "65_Assessments",
    "66_Services", "67_Orgs",
    "90_Meta",
]


def load_fm_safely(md_path: Path):
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    while lines and (lines[0].strip().startswith("<!--") or lines[0].strip() == ""):
        lines.pop(0)
    cleaned = "\n".join(lines)
    try:
        return frontmatter.loads(cleaned), content
    except Exception:
        return None, content


def iter_vault_mds():
    for md in VAULT.rglob("*.md"):
        rel = md.relative_to(VAULT)
        rel_str = str(rel)
        if any(rel_str.startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        if rel_str in EXCLUDE_FILES:
            continue
        parts = rel.parts
        if parts[0] in {".obsidian", ".claude", ".github", "docs", "mcp_server"}:
            continue
        if "raw" in parts or "templates" in parts:
            continue
        if "health-reports" in parts or "amendment-reports" in parts:
            continue
        yield md


def parse_date(v):
    if isinstance(v, (date, datetime)):
        return v if isinstance(v, date) else v.date()
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def collect_stats():
    layer_counts: Counter = Counter()
    type_counts: Counter = Counter()
    status_counts: Counter = Counter()
    pending: list = []
    expired: list = []
    due_soon: list = []
    in_degree: Counter = Counter()
    total_relations = 0
    total_notes = 0

    today_d = date.today()

    notes_meta: dict = {}

    for md in iter_vault_mds():
        rel = str(md.relative_to(VAULT))
        post, _ = load_fm_safely(md)
        if not post:
            continue
        meta = post.metadata or {}
        nid = str(md.relative_to(VAULT).with_suffix(""))
        layer = rel.split("/", 1)[0]
        layer_counts[layer] += 1
        total_notes += 1

        t = meta.get("type", "")
        if t:
            type_counts[t] += 1
        status = meta.get("status", "active")
        status_counts[status] += 1

        notes_meta[nid] = {
            "title": meta.get("title") or md.stem,
            "layer": layer,
            "type": t,
            "status": status,
        }

        # 改正追随状況
        if status == "pending-amendment":
            pending.append((nid, meta.get("title") or md.stem, str(meta.get("review_due", "未設定"))))
        rd = parse_date(meta.get("review_due"))
        if rd:
            delta = (rd - today_d).days
            if delta < 0 and status != "archived":
                expired.append((nid, -delta))
            elif delta <= 90 and status != "archived":
                due_soon.append((nid, delta))

        # 被参照カウント
        relations = meta.get("relations") or []
        if isinstance(relations, list):
            total_relations += len(relations)
            for r in relations:
                if not isinstance(r, dict):
                    continue
                target = r.get("to", "")
                m = re.match(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]", target.strip())
                if m:
                    in_degree[m.group(1).strip()] += 1

    return {
        "layer_counts": layer_counts,
        "type_counts": type_counts,
        "status_counts": status_counts,
        "pending": pending,
        "expired": expired,
        "due_soon": due_soon,
        "in_degree": in_degree,
        "notes_meta": notes_meta,
        "total_relations": total_relations,
        "total_notes": total_notes,
    }


def git_recent_changes(limit: int = 15) -> list:
    try:
        out = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h|%ad|%s", "--date=short"],
            cwd=VAULT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode != 0:
            return []
        lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
        return [tuple(ln.split("|", 2)) for ln in lines]
    except Exception:
        return []


def build_mermaid(stats: dict) -> str:
    """層間の関係密度を Mermaid で可視化"""
    # 層ペアの接続数を数える
    edges: dict = defaultdict(int)
    for md in iter_vault_mds():
        post, _ = load_fm_safely(md)
        if not post:
            continue
        src_layer = str(md.relative_to(VAULT)).split("/", 1)[0]
        relations = post.metadata.get("relations") or []
        if not isinstance(relations, list):
            continue
        for r in relations:
            if not isinstance(r, dict):
                continue
            target = r.get("to", "")
            m = re.match(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]", target.strip())
            if not m:
                continue
            t = m.group(1).strip()
            # target が "60_Laws/foo" 形式なら層を抽出
            if "/" in t:
                tgt_layer = t.split("/", 1)[0]
            else:
                continue
            if src_layer == tgt_layer:
                continue  # 同一層内はスキップ
            if src_layer in LAYER_ORDER and tgt_layer in LAYER_ORDER:
                edges[(src_layer, tgt_layer)] += 1

    # Mermaid 形式に変換
    lines = ["```mermaid", "graph LR"]
    # ノード定義
    for layer in LAYER_ORDER:
        if layer in stats["layer_counts"]:
            count = stats["layer_counts"][layer]
            safe = layer.replace("_", "")
            lines.append(f'    {safe}["{layer}<br/>({count})"]')

    # エッジ（閾値: 3 以上）
    for (s, t), w in sorted(edges.items(), key=lambda x: -x[1]):
        if w < 3:
            continue
        s_safe = s.replace("_", "")
        t_safe = t.replace("_", "")
        lines.append(f"    {s_safe} -->|{w}| {t_safe}")

    lines.append("```")
    return "\n".join(lines)


def generate_overview(stats: dict) -> str:
    today_d = date.today()
    recent = git_recent_changes(15)
    mermaid = build_mermaid(stats)

    lines = []
    R = lines.append

    R("<!-- allow-realname -->")
    R("---")
    R("type: meta")
    R(f"updated: {today_d.isoformat()}")
    R("tags: [meta, overview]")
    R("cssclasses: [layer-meta]")
    R("---")
    R("")
    R("# welfare-graph 俯瞰ダッシュボード")
    R("")
    R(f"**最終更新**: {today_d.isoformat()}（`generate_overview.py` により自動生成）")
    R("")
    R("本ファイルは [[CLAUDE#§3 動作モード（5 + 2）]] の overview モード出力。")
    R("手動編集は行わず、`python3 90_Meta/scripts/generate_overview.py` で再生成すること。")
    R("")
    R("---")
    R("")

    # サマリ
    R("## 📊 全体サマリ")
    R("")
    R(f"- **総ノート数**: {stats['total_notes']}")
    R(f"- **総 relations**: {stats['total_relations']}")
    R(f"- **平均 relations/ノート**: {stats['total_relations'] / max(stats['total_notes'], 1):.1f}")
    R("")

    # 層別
    R("## 🗂 層別ページ数")
    R("")
    R("| 層 | 件数 |")
    R("|---|---|")
    for layer in LAYER_ORDER:
        count = stats["layer_counts"].get(layer, 0)
        if count > 0:
            R(f"| {layer} | {count} |")
    R("")

    # type 別
    R("## 📑 type 別ページ数")
    R("")
    R("| type | 件数 |")
    R("|---|---|")
    for t, c in stats["type_counts"].most_common():
        R(f"| {t} | {c} |")
    R("")

    # status 別
    R("## 🔄 status 別ページ数")
    R("")
    R("| status | 件数 |")
    R("|---|---|")
    for s, c in stats["status_counts"].most_common():
        R(f"| {s} | {c} |")
    R("")

    # 改正追随
    R("## 🚨 改正追随状況")
    R("")
    R(f"- pending-amendment（改正予告中）: {len(stats['pending'])} 件")
    R(f"- review_due 超過: {len(stats['expired'])} 件")
    R(f"- 3 か月以内に review_due: {len(stats['due_soon'])} 件")
    R("")
    if stats["pending"]:
        R("### 改正予告中")
        for nid, title, rd in stats["pending"]:
            R(f"- [[{nid}]] — review_due: {rd}")
        R("")
    if stats["expired"]:
        R("### review_due 超過")
        for nid, days in stats["expired"]:
            R(f"- [[{nid}]] — 超過 {days} 日")
        R("")
    if stats["due_soon"]:
        R("### 3 か月以内")
        for nid, days in sorted(stats["due_soon"], key=lambda x: x[1]):
            R(f"- [[{nid}]] — 残り {days} 日")
        R("")

    # 被参照 Top
    R("## 🔗 被参照ノート Top 15")
    R("")
    R("| 順位 | ノート | 被参照数 |")
    R("|---|---|---|")
    for i, (nid, c) in enumerate(stats["in_degree"].most_common(15), 1):
        R(f"| {i} | [[{nid}]] | {c} |")
    R("")

    # 最近の変更
    R("## 📅 最近の変更（git log 直近 15 件）")
    R("")
    if recent:
        R("| commit | date | message |")
        R("|---|---|---|")
        for h, d, msg in recent:
            msg_esc = msg.replace("|", "\\|")
            R(f"| `{h}` | {d} | {msg_esc} |")
    else:
        R("（git 履歴取得不可）")
    R("")

    # Mermaid 層間関係
    R("## 🕸 層間関係グラフ（Mermaid）")
    R("")
    R("relations が 3 件以上ある層間接続を表示。数字は接続数。")
    R("")
    R(mermaid)
    R("")

    # フッター
    R("---")
    R("")
    R("## 🔧 再生成")
    R("")
    R("```bash")
    R("python3 90_Meta/scripts/generate_overview.py")
    R("```")
    R("")
    R("関連: [[CLAUDE]] / [[90_Meta/SCHEMA]] / [[90_Meta/amendment-tracking]] / [[README]]")

    return "\n".join(lines)


def main():
    print(f"vault: {VAULT}")
    print("overview.md 生成中...")
    stats = collect_stats()
    overview = generate_overview(stats)
    out_path = VAULT / "overview.md"
    out_path.write_text(overview, encoding="utf-8")
    print(f"✅ 生成完了: {out_path.name}")
    print(f"  ノート: {stats['total_notes']} / 関係: {stats['total_relations']}")
    print(f"  改正予告中: {len(stats['pending'])} / 期限超過: {len(stats['expired'])}")


if __name__ == "__main__":
    main()
