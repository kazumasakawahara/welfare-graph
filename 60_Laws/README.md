<!-- allow-realname -->
---
type: layer-readme
layer: laws
tags: [layer, laws]
cssclasses: [layer-meta]
---

# 60_Laws — 法令

計画相談業務の根拠となる法令。条文要約・定義・通報義務・罰則などを構造化して収納する。

## 対象範囲
- 障害者総合支援法
- 障害者虐待防止法
- 障害者差別解消法
- 発達障害者支援法
- 精神保健福祉法
- 知的障害者福祉法
- 身体障害者福祉法
- 児童福祉法（障害児関連条項）
- 成年後見制度関連（民法・任意後見契約法）
- 障害年金関連（国民年金法・厚生年金保険法）
- 生活保護法
- 医療観察法

## 命名規則
`60_Laws/{法令略称}.md` 例: `障害者総合支援法.md`

## 必須 frontmatter
`90_Meta/SCHEMA.md` の `law` セクション参照。`source_url` / `version` / `effective_date` / `review_due` は **必須**。

## 運用
- 原文PDF・公式資料は `raw/laws/` に保存（要約元）
- 条文要約は LLM 生成可だが、解釈部分は必ず出典明示
- 報酬改定・法改正（原則3年周期）時は `review_due` を更新
