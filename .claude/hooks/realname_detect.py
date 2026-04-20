#!/usr/bin/env python3
"""
実名検出 PreToolUse hook
Write/Edit ツール呼び出し時に、ノート内容に実名らしき文字列が含まれていないか検査する。

検出ルール:
  1. 漢字フルネーム: 姓2-4文字 + 空白 + 名2-4文字（例: 山田 太郎）
  2. 漢字フルネーム（空白なし）: 漢字3-6文字（姓名連結）
  3. カタカナフルネーム: カタカナ2-8文字 + 空白 + カタカナ2-8文字
  4. 電話番号らしき数字列

許可例外:
  - 90_Meta/alias_map.md（仮名マップ本体）
  - サンプル・テンプレート内の「山田 太郎」等の例示

結果:
  - 疑わしい文字列があればブロックし、修正を促す
  - 「例示」として許可する場合は、本文に `<!-- allow-realname -->` を入れる
"""
import json
import re
import sys
from pathlib import Path

ALLOW_PATHS = [
    "90_Meta/alias_map.md",
]

SAMPLE_NAMES_WHITELIST = {"山田 太郎", "山田 花子", "山田太郎", "山田花子"}

# 姓として出現しにくい頻出語（誤検出削減）
STOPWORDS_LEADING = {
    "本日", "昨日", "今日", "明日", "今週", "先週", "来週",
    "今月", "先月", "来月", "今年", "昨年", "来年",
    "午前", "午後", "朝", "夕方", "夜間",
    "訪問", "面談", "相談", "同行", "記録", "報告",
    "本人", "家族", "両親", "父親", "母親", "姉妹", "兄弟",
    "事業", "事業所", "医療", "病院", "医師", "担当",
    "注意", "重要", "参考", "例示", "備考",
}

KANJI = r"[\u4e00-\u9fff々〆ヵヶ]"
KATAKANA = r"[\u30a1-\u30fa\u30fc]"

PATTERNS = [
    (re.compile(rf"(?=({KANJI}{{2,4}})[\s\u3000]+({KANJI}{{2,4}}))"), "漢字フルネーム（空白区切り）"),
    (re.compile(rf"(?=({KATAKANA}{{2,8}})[\s\u3000]+({KATAKANA}{{2,8}}))"), "カタカナフルネーム"),
    (re.compile(r"0\d{1,4}-\d{1,4}-\d{3,4}"), "電話番号"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")

    for allow in ALLOW_PATHS:
        if allow in file_path:
            return 0

    if "90_Meta/templates/" in file_path:
        return 0

    content = tool_input.get("content") or tool_input.get("new_string") or ""
    if not content:
        return 0

    if "<!-- allow-realname -->" in content:
        return 0

    findings = []
    seen = set()
    for pattern, label in PATTERNS:
        for m in pattern.finditer(content):
            if m.groups():
                first, second = m.group(1), m.group(2)
                text = f"{first} {second}"
            else:
                text = m.group(0)
            text = text.strip()
            if not text or text in seen:
                continue
            if text in SAMPLE_NAMES_WHITELIST:
                continue
            if "フルネーム" in label and m.groups():
                if m.group(1) in STOPWORDS_LEADING:
                    continue
            seen.add(text)
            findings.append(f"  - [{label}] '{text}'")

    if not findings:
        return 0

    msg = (
        "⚠️  実名らしき文字列を検出しました。vault内は仮名IDのみで運用してください。\n"
        + "\n".join(findings)
        + "\n\n対応:\n"
        "  1. 実名は `90_Meta/alias_map.md`（Meld Encrypt暗号化済）にのみ記載\n"
        "  2. ノート本文は仮名ID（P-XXXX / F-XXXX 等）に置換\n"
        "  3. 意図的な例示の場合は本文に `<!-- allow-realname -->` を挿入\n"
    )
    print(msg, file=sys.stderr)
    return 2  # block


if __name__ == "__main__":
    sys.exit(main())
