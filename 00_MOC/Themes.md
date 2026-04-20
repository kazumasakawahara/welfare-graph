<!-- allow-realname -->
---
type: moc
cssclasses: [layer-moc]
tags: [moc, insights]
---

# Themes - 知見テーマ一覧

蓄積された知見（30_Insights）のテーマ別ビュー。

## 信頼度別
```dataview
TABLE theme, evidence_count, updated
FROM "30_Insights"
SORT confidence DESC, evidence_count DESC
```

## 最近追加された知見
```dataview
LIST
FROM "30_Insights"
SORT created DESC
LIMIT 10
```

## 推奨テーマ（例）
- 感覚過敏と環境調整
- パニック時の初動
- 家族（特に母）の負担兆候
- きょうだいへの説明
- 日生事業の契約判断ライン
- 住まいの選択肢（GH / 一人暮らし / 入所）
- 医療アクセス（協力的な主治医の見つけ方）
- 意思決定支援
