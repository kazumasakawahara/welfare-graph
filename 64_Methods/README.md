<!-- allow-realname -->
---
type: layer-readme
layer: methods
tags: [layer, methods]
cssclasses: [layer-meta]
---

# 64_Methods — 支援技法

実際の支援現場で使う具体的な方法論。エビデンスレベルを明記して収納。

## 対象範囲
- 構造化支援（TEACCHプログラム）
- PECS（絵カード交換式コミュニケーション）
- 応用行動分析（ABA）
- ペアレントトレーニング
- SST（ソーシャルスキルトレーニング）
- 認知行動療法（CBT）
- 強度行動障害支援
- 環境調整法
- ポジティブ行動支援（PBS）
- 感覚統合療法
- アンガーマネジメント
- マインドフルネス
- リロケーション支援
- 意思決定支援会議
- 金銭管理支援（日常生活自立支援事業）
- 危機介入

## 命名規則
`64_Methods/{技法名}.md`

## 必須 frontmatter
`evidence_level`（high / moderate / low / emerging）/ `target_disorder`（対象障害のIDリスト）/ `training_required`（研修要否）。

## 運用
- 技法↔障害特性は `responds-to`（適応）/ `contraindicated`（禁忌）でリンク
- 技法↔理論（`62_Frameworks/`）は `underpinned-by` でリンク
- 実施に研修資格が要るものは `training_required: true` を明示
- エビデンスのない「流行り」を区別するため `evidence_level: emerging` を活用
