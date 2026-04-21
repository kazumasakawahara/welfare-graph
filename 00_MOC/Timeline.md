<!-- allow-realname -->
---
type: moc
tags: [moc, timeline]
updated: 2026-04-21
cssclasses: [layer-moc]
---

# Timeline - エピソード・制度タイムライン

## 権利擁護・合理的配慮のタイムライン

障害者権利擁護に関する主要な国際規範・国内法改正・判例の時系列:

| 年 | 出来事 | ノート |
|---|---|---|
| 2006 | 国連総会 障害者権利条約 採択 | [[60_Laws/障害者権利条約]] |
| 2007 | 日本 条約署名 | — |
| 2008 | 条約発効 | — |
| 2011 | 障害者基本法 大幅改正（社会モデル・差別禁止規定の導入） | [[60_Laws/障害者基本法]] |
| 2013 | 障害者差別解消法 制定 / 雇用促進法 改正（合理的配慮義務） | [[60_Laws/障害者差別解消法]] / [[60_Laws/障害者雇用促進法]] |
| 2014 | 日本 条約批准（2月19日発効） | [[60_Laws/障害者権利条約]] |
| 2016 | 障害者差別解消法 施行（行政義務・事業者努力義務） | [[60_Laws/障害者差別解消法]] |
| 2018 | 精神障害者の雇用義務化（雇用促進法） | [[60_Laws/障害者雇用促進法]] |
| 2020 | 川崎就学訴訟 横浜地裁判決（令和2年3月18日） | [[30_Insights/川崎就学訴訟_インクルーシブ教育と合理的配慮]] |
| 2021 | 医療的ケア児支援法 制定・施行（9月18日） | [[60_Laws/医療的ケア児支援法]] |
| 2021 | 障害者差別解消法 令和3年改正（事業者義務化） | [[60_Laws/障害者差別解消法]] |
| 2022 | Man to Man Animo 事件 岐阜地裁判決（令和4年8月30日） | [[30_Insights/Man_to_Man_Animo事件_雇用における合理的配慮義務]] |
| 2022 | 国連 障害者権利委員会 第1回対日審査 総括所見公表 | [[60_Laws/障害者権利条約]] |
| 2024 | 障害者差別解消法 事業者の合理的配慮義務化 施行（4月1日） | [[60_Laws/障害者差別解消法]] |
| 2024 | 就労選択支援 創設施行（10月1日） | [[66_Services/就労選択支援]] / [[61_Guidelines/就労選択支援_運営要綱]] |
| 2026 | 雇用促進法 法定雇用率 2.7%引上げ 予定（7月） | [[60_Laws/障害者雇用促進法]] |

## エピソード時系列

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
