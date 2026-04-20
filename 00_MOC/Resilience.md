---
type: moc
tags: [moc, resilience]
cssclasses: [layer-moc]
---

# Resilience - 親亡き後設計

## CareRole 棚卸し状況（人物別）
```dataview
TABLE role, current_holder, risk_level, substitute_status
FROM "50_Resilience/CareRoles"
SORT person, risk_level DESC
```

## 高リスク / 代替未検討
```dataview
TABLE person, role, current_holder
FROM "50_Resilience/CareRoles"
WHERE (risk_level = "high" OR risk_level = "critical") AND substitute_status = "未検討"
```

## 代替手段（Substitutes）
```dataview
TABLE person, provider_type, status, escalation_trigger
FROM "50_Resilience/Substitutes"
SORT person
```

## 日常生活自立支援事業の利用状況
```dataview
TABLE person, status, started, monthly_fee
FROM "50_Resilience/Substitutes"
WHERE provider_type = "日常生活自立支援事業"
```

## シミュレーション
```dataview
TABLE person, scenario, coverage_score, updated
FROM "50_Resilience/Simulations"
SORT coverage_score ASC
```
