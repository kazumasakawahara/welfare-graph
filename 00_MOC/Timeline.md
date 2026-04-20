---
type: moc
tags: [moc, timeline]
cssclasses: [layer-moc]
---

# Timeline - エピソード時系列

## 最近のエピソード（直近30件）
```dataview
TABLE person, severity, mood
FROM "20_Episodes"
SORT file.name DESC
LIMIT 30
```

## 重大度: high / critical
```dataview
TABLE person, date, file.link
FROM "20_Episodes"
WHERE severity = "high" OR severity = "critical"
SORT date DESC
```

## 今月のエピソード数（人物別）
```dataview
TABLE length(rows) AS 件数
FROM "20_Episodes"
WHERE startswith(string(date), string(date(today)).substring(0,7))
GROUP BY person
```
