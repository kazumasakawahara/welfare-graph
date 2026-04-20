<!-- allow-realname -->
---
type: layer-readme
layer: assessments
tags: [layer, assessments]
cssclasses: [layer-meta]
---

# 65_Assessments — アセスメントツール

支援区分認定・計画作成・モニタリングで使う評価尺度と手法。

## 対象範囲
- 障害支援区分認定調査（80項目）
- 行動関連項目（12項目）
- 医師意見書
- ICF評価ツール
- Vineland-II 適応行動尺度
- WAIS-IV / WISC-V（知能検査）
- PARS-TR（広汎性発達障害日本自閉症協会評定尺度）
- CARS2（小児自閉症評定尺度）
- SDQ（子どもの強さと困難さアンケート）
- S-M社会生活能力検査
- MAS（動機アセスメントスケール）
- ABC分析（先行事象・行動・結果）
- エコマップ
- ジェノグラム
- ライフラインチャート
- ニーズ整理票
- リスクアセスメントシート

## 命名規則
`65_Assessments/{ツール名}.md`

## 必須 frontmatter
`administrator`（実施者資格）/ `time_required`（実施所要時間）/ `purpose`（用途）。

## 運用
- 支援区分認定 → サービス適格判定のチェーンを明示（`65` → `66_Services/`）
- 心理検査は実施者に資格要件あり（`administrator` 必須）
- 結果の解釈は専門職に委ね、計画相談では「結果をもとに支援方針を立てる」視点で記述
