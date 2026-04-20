---
type: person
id: P-XXXX
status: active
diagnosis: []        # 例: 知的障害（中度）, 自閉スペクトラム症
disability_cert: ""  # 療育手帳 A/B, 精神障害者保健福祉手帳 X級 等
service_plan_id: ""  # サービス等利用計画の識別
primary_supporter: "" # 現在の主たる支援者（家族仮名ID）
created: {{date}}
updated: {{date}}
tags: [person]
cssclasses: [layer-person]
---

# {{title}}

## 基本情報
- 年齢 / 性別:
- 居住形態:
- 収入:

## 強み（Strengths）
-

## 禁忌 / 苦手（Contraindications）
-

## 推奨ケア（Preferred Care）
-

## コミュニケーション特性
-

## 関係者
- 家族: [[F-XXXX]]
- 事業所: [[O-XXXX]]
- 医療: [[M-XXXX]]
- 後見等:
- 社協:
- 相談支援: [[C-XXXX]]

## 最近のエピソード
```dataview
LIST
FROM "20_Episodes"
WHERE contains(file.name, this.id)
SORT file.name DESC
LIMIT 10
```

## 関連する知見
```dataview
LIST
FROM "30_Insights"
WHERE contains(file.outlinks, this.file.link)
```

## CareRole（親亡き後設計）
```dataview
TABLE current_holder, substitute_status
FROM "50_Resilience/CareRoles"
WHERE contains(file.name, this.id)
```
