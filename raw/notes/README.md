<!-- allow-realname -->
# raw/notes/

会話保存モード（[[../../CLAUDE#§9 会話保存モード（save）]]）の保存先。
Claude Desktop / Claude Code 等での議論・手書きメモ・会議記録を保管する。

## 命名規則

```
raw/notes/YYYY-MM-DD_トピック名.md
```

例:
- `raw/notes/2026-04-25_就労選択支援の運用課題.md`
- `raw/notes/2026-05-10_モニタリング頻度見直し議論.md`
- `raw/notes/2026-06-01_性教育研修計画.md`

## 必須 frontmatter

```yaml
---
type: conversation
date: YYYY-MM-DD
source: claude.ai | claude-desktop | claude-code | manual
participants: [河原, Claude]
tags: [raw, notes, conversation]
---
```

## 内容構造（推奨）

```markdown
# {トピック}

## 背景・経緯

## 議論の要点
- ...
- ...

## 決定事項・結論
- ...

## 未解決事項・次のアクション
- [ ] ...
- [ ] ...

## 関連ノート
- [[60_Laws/...]]
- [[66_Services/...]]

## 生会話ログ（任意）
（構造化前の raw テキストを残したい場合）
```

## 運用ルール

- **raw/ は READ-ONLY**: 一度保存したら編集しない（[[../../CLAUDE#§2 絶対遵守のガードレール]] 第 1 項）
- **個人情報は保存前に匿名化**: [[../../CLAUDE#§7 個人情報の匿名化ルール]]
- **会話の「流れ」より「知見」を優先**: 試行錯誤の過程ではなく結論と根拠を残す
- **後続の ingest で wiki 層へ**: `raw-to-wiki` スキル経由で 30_Insights/ 等に昇華

## 取り込み（ingest）先の目安

| 内容 | 取り込み先 |
|---|---|
| 支援上の一般的知見 | `30_Insights/` |
| 法令解釈の議論 | `60_Laws/` の該当ノート本文に追記 |
| 運用ノウハウ | `90_Meta/` または該当スキル |
| 事例パターン | `30_Insights/` |

詳細: [`.claude/skills/conversation-save/SKILL.md`](../../.claude/skills/conversation-save/SKILL.md)
