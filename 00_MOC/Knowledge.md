<!-- allow-realname -->
---
type: moc
tags: [moc, knowledge]
updated: 2026-04-20
cssclasses: [layer-moc]
---

# Knowledge — 知識層ルーター

計画相談専門員が使う公的知識のインデックス。利用者ノート（P-XXXX）からこの層へ `relations` でリンクし、根拠付きの支援提案に繋げる。

## 9層アーキテクチャ

```
人物・記録（既存）                       知識（新設）
────────────────────                   ────────────────────
10_People/       利用者 P-XXXX          60_Laws/         法令
20_Episodes/     エピソード              61_Guidelines/   ガイドライン・手引
30_Insights/     抽象化知見              62_Frameworks/   理論・フレームワーク
40_Stakeholders/ 具体関係者              63_Disorders/    障害特性
50_Resilience/   親亡き後設計            64_Methods/      支援技法
                                        65_Assessments/  アセスメントツール
                                        66_Services/     サービス・社会資源
                                        67_Orgs/         関係機関（類型）
```

## 各層の入口

| 層 | 主な用途 | 入口 |
|---|---|---|
| 法令 | 根拠・義務・罰則 | [[60_Laws/README]] |
| ガイドライン | 運用基準・記録要件 | [[61_Guidelines/README]] |
| 理論 | 支援思想・判断基準 | [[62_Frameworks/README]] |
| 障害特性 | 診断・生活機能への影響 | [[63_Disorders/README]] |
| 支援技法 | 具体的方法論・エビデンス | [[64_Methods/README]] |
| アセスメント | 評価尺度・手法 | [[65_Assessments/README]] |
| サービス | 制度・資源・適格要件 | [[66_Services/README]] |
| 関係機関 | 連携先・紹介経路 | [[67_Orgs/README]] |

## LLMルーター（典型パス）

### パス A: 利用者から支援提案へ
```
[[P-XXXX]]
  └─ has-characteristic → [[63_Disorders/ASD]]
       └─ responds-to → [[64_Methods/構造化支援]]
            └─ underpinned-by → [[62_Frameworks/TEACCH]]
  └─ eligible-service → [[66_Services/行動援護]]
       └─ mandated-by → [[60_Laws/障害者総合支援法]]
       └─ provided-by → [[67_Orgs/指定特定相談支援事業所]]
```

### パス B: 虐待兆候検知から通報へ
```
[[20_Episodes/YYYY-MM-DD]]
  └─ mandatory-report-trigger → [[60_Laws/障害者虐待防止法]]
       └─ compliance-required → [[61_Guidelines/虐待防止マニュアル]]
       └─ escalate-to → [[67_Orgs/市町村障害福祉主管課]]
```

### パス C: 計画作成からモニタリングへ
```
[[P-XXXX]]
  └─ assessment → [[65_Assessments/障害支援区分認定調査]]
       └─ eligible-service → [[66_Services/行動援護]]
            └─ compliance-required → [[61_Guidelines/モニタリング標準期間通知]]
```

## テーマ別MOC（横断ハブ）

特定テーマで層を横断する論点をまとめたMOC:

- [[Sexuality]] — 知的障害のある人の性と教育（権利・教育・予防・対応の4柱）

### 権利擁護・合理的配慮

[[62_Frameworks/合理的配慮]] を概念ハブとする論点群。法令階層:

1. 国際規範: [[60_Laws/障害者権利条約]]（2006 国連採択）
2. 国内基本法: [[60_Laws/障害者基本法]]（4条 差別禁止・16条 教育）
3. 国内特別法:
    - [[60_Laws/障害者差別解消法]]（事業者の合理的配慮義務・令和6年4月義務化）
    - [[60_Laws/障害者雇用促進法]]（雇用領域の特則・36条の2-4）
    - [[60_Laws/医療的ケア児支援法]]（令和3年・インクルーシブ教育を前進）

具体事例:

- 教育領域の判例 → [[30_Insights/川崎就学訴訟_インクルーシブ教育と合理的配慮]]
- 雇用領域の判例 → [[30_Insights/Man_to_Man_Animo事件_雇用における合理的配慮義務]]

適用されやすい障害特性: [[63_Disorders/高次脳機能障害]] / [[63_Disorders/強迫性障害]] / [[63_Disorders/重症心身障害]] 他

## スキーマ

frontmatter 仕様と `relations` リンク型辞書は [[SCHEMA]] 参照。

## 運用ルール

1. **出典主義**: 法令・ガイドライン・サービスページには `source_url` / `version` / `effective_date` を必ず記載
2. **免責**: LLM生成の支援提案には「最終判断は行政・弁護士・主治医に確認」を添える
3. **期限管理**: `review_due` を設定し、`data-quality-agent` で定期監視
4. **仮名化**: 利用者情報は全て P-XXXX 等の仮名IDで記述
5. **孤児防止**: 新規ノート作成時は最低1つの `relations` を張る

## 関連スキル

- `wiki-query-hybrid`: 知識層を跨いだ横断検索
- `visit-prep`: 訪問前ブリーフィング（利用者×関連知識）
- `emergency-protocol`: 緊急時の法令・連携先の自動提示
- `insight-agent`: エピソード→知見抽出
- `data-quality-agent`: `review_due` 監視
- `realname-check`: 実名混入検査

## 未整備ページ一覧
```dataview
LIST
FROM "60_Laws" OR "61_Guidelines" OR "62_Frameworks" OR "63_Disorders" OR "64_Methods" OR "65_Assessments" OR "66_Services" OR "67_Orgs"
WHERE file.name = "README" OR length(relations) = 0
```
