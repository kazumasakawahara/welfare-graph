#!/usr/bin/env /usr/bin/python3
"""
add_cssclasses.py
既存の全ノートに frontmatter.type を元に cssclasses: [layer-*] を追加する。

冪等（既に追加されていれば重複しない）。実名リスク: 書き換えのみ行い、内容は保存前後で比較。
"""

import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {".obsidian", ".claude", "raw"}
EXCLUDE_FILES = {"90_Meta/alias_map.md"}

# type → cssclasses
TYPE_TO_CLASS = {
    "law": "layer-law",
    "guideline": "layer-guideline",
    "framework": "layer-framework",
    "disorder": "layer-disorder",
    "method": "layer-method",
    "assessment": "layer-assessment",
    "service": "layer-service",
    "org": "layer-org",
    "person": "layer-person",
    "moc": "layer-moc",
    "insight": "layer-insight",
    "meta": "layer-meta",
    "care-role": "layer-resilience",
    "care_role": "layer-resilience",
    "substitute": "layer-resilience",
    "simulation": "layer-resilience",
    "stakeholder": "layer-stakeholder",
    "episode": "layer-episode",
    "layer-readme": "layer-meta",
    "alias_map": "layer-meta",
}


def iter_vault_mds():
    for md in VAULT.rglob("*.md"):
        rel = md.relative_to(VAULT)
        parts = rel.parts
        if any(str(rel).startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        if str(rel) in EXCLUDE_FILES:
            continue
        if parts[0] in {".obsidian", ".claude"}:
            continue
        yield md


def parse_frontmatter_block(content: str):
    """`---\n...\n---\n` 形式の frontmatter 本体を抽出。戻り値: (pre, fm_text, post, offsets)"""
    # 先頭の HTML コメント/空行を pre に
    lines = content.splitlines(keepends=True)
    pre = []
    idx = 0
    while idx < len(lines):
        s = lines[idx].strip()
        if s.startswith("<!--") or s == "":
            pre.append(lines[idx])
            idx += 1
        else:
            break

    if idx >= len(lines) or lines[idx].strip() != "---":
        return "".join(pre), None, content[len("".join(pre)):]

    # frontmatter 開始
    fm_start = idx + 1
    fm_end = None
    j = fm_start
    while j < len(lines):
        if lines[j].strip() == "---":
            fm_end = j
            break
        j += 1
    if fm_end is None:
        return "".join(pre), None, content[len("".join(pre)):]

    fm_text = "".join(lines[fm_start:fm_end])
    post = "".join(lines[fm_end + 1:])
    pre_text = "".join(pre) + lines[idx]  # 最後の `---` も pre に含める
    return pre_text, fm_text, post


def extract_type(fm_text: str) -> str:
    """fm_text から type の値を取得（単純 regex）"""
    m = re.search(r"^type:\s*(\S+)\s*$", fm_text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")
    return ""


def has_cssclasses(fm_text: str) -> bool:
    return re.search(r"^cssclasses:", fm_text, flags=re.MULTILINE) is not None


def add_cssclasses(fm_text: str, css_class: str) -> str:
    """frontmatter 末尾に cssclasses: [css_class] を追加（末尾 `\n` 保証）"""
    if not fm_text.endswith("\n"):
        fm_text = fm_text + "\n"
    return fm_text + f"cssclasses: [{css_class}]\n"


def process_file(md: Path) -> str:
    """処理結果: 'updated' / 'skipped-no-fm' / 'skipped-has-css' / 'skipped-no-type' / 'skipped-unknown-type'"""
    original = md.read_text(encoding="utf-8")
    pre, fm_text, post = parse_frontmatter_block(original)

    if fm_text is None:
        return "skipped-no-fm"

    if has_cssclasses(fm_text):
        return "skipped-has-css"

    t = extract_type(fm_text)
    if not t:
        return "skipped-no-type"

    css = TYPE_TO_CLASS.get(t)
    if not css:
        return f"skipped-unknown-type:{t}"

    new_fm = add_cssclasses(fm_text, css)
    # pre は `---\n` まで含まれているので、 + new_fm + `---\n` + post
    new_content = pre + new_fm + "---\n" + post
    md.write_text(new_content, encoding="utf-8")
    return f"updated:{css}"


def main():
    results = {"updated": 0, "skipped-has-css": 0, "skipped-no-fm": 0, "skipped-no-type": 0, "skipped-unknown": 0}
    details = []

    for md in iter_vault_mds():
        rel = str(md.relative_to(VAULT))
        r = process_file(md)
        if r.startswith("updated"):
            results["updated"] += 1
            details.append(f"✓ {rel}: {r}")
        elif r == "skipped-has-css":
            results["skipped-has-css"] += 1
        elif r == "skipped-no-fm":
            results["skipped-no-fm"] += 1
        elif r == "skipped-no-type":
            results["skipped-no-type"] += 1
        else:
            results["skipped-unknown"] += 1
            details.append(f"? {rel}: {r}")

    for d in details:
        print(d)

    print(f"\n=== サマリ ===")
    print(f"  更新: {results['updated']}")
    print(f"  スキップ（既にcss済）: {results['skipped-has-css']}")
    print(f"  スキップ（frontmatter なし）: {results['skipped-no-fm']}")
    print(f"  スキップ（type なし）: {results['skipped-no-type']}")
    print(f"  スキップ（type 未対応）: {results['skipped-unknown']}")


if __name__ == "__main__":
    main()
