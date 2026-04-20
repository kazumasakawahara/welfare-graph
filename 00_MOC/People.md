---
type: moc
tags: [moc, people]
cssclasses: [layer-moc]
---

# People - 当事者一覧

## Active
```dataview
TABLE diagnosis, disability_cert, primary_supporter, updated
FROM "10_People"
WHERE status = "active"
SORT updated DESC
```

## Inactive / アーカイブ
```dataview
LIST
FROM "10_People"
WHERE status != "active"
```

## 未更新アラート（90日以上）
```dataview
LIST
FROM "10_People"
WHERE status = "active" AND date(today) - date(updated) > dur(90 days)
```
