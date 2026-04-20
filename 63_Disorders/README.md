<!-- allow-realname -->
---
type: layer-readme
layer: disorders
tags: [layer, disorders]
cssclasses: [layer-meta]
---

# 63_Disorders — 障害特性・疾患

利用者の困り感の背景にある障害特性。DSM-5-TR / ICD-11 準拠で記述。

## 対象範囲
- 知的障害（軽度・中度・重度・最重度）
- 自閉スペクトラム症（ASD）
- 注意欠如・多動症（ADHD）
- 限局性学習症（SLD）
- 発達性協調運動症（DCD）
- 強度行動障害
- 統合失調症
- 双極症
- うつ病
- 不安症群
- 高次脳機能障害
- てんかん
- ダウン症候群
- 重症心身障害
- 医療的ケア児者
- 難病（指定難病・小児慢性特定疾病）

## 命名規則
`63_Disorders/{障害名}.md`

## 必須 frontmatter
`icd11_code` / `dsm5_code` / `prevalence` / `onset_typical`。

## 運用
- 診断基準と支援の距離を意識（診断名≠支援必要度）
- 障害↔支援技法（`64_Methods/`）は `responds-to` / `contraindicated` でリンク
- 併存しやすい障害は `comorbid-with` でリンク
- 「診断ではなく生活機能」を重視する記述を心がける
