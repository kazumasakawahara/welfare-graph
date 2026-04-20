---
type: care_role
person: P-XXXX
role: ""                   # 例: 金銭管理 / 服薬管理 / 通院同行 / 情緒的支え
current_holder: F-XXXX     # 現在誰が担っているか
risk_level: medium         # low / medium / high / critical
substitute_plan: ""        # 代替候補（S-XXXX 等）
substitute_status: 未検討    # 未検討 / 検討中 / 契約準備中 / 契約済 / 稼働中
transition_trigger: ""     # 代替に移行する条件
updated: {{date}}
tags: [care_role, resilience]
cssclasses: [layer-resilience]
---

# {{person}} の CareRole: {{role}}

## 現状
- 担い手: [[{{current_holder}}]]
- 頻度・内容:
- 担い手が失われた場合の影響:

## リスク評価
- `risk_level`: {{risk_level}}
- 根拠:

## 代替手段の設計
- 候補: [[]]
- 移行ステップ:
  1.
  2.
- 移行のハードル（費用・手続・本人の受容等）:

## 関連 Substitute ノート
- [[]]
