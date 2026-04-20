<!-- allow-realname -->
---
type: meta
title: SCHEMA
tags: [meta, schema]
updated: 2026-04-20
cssclasses: [layer-meta]
---

# SCHEMA — frontmatter 仕様 と リンク型辞書

このvault内の全ノートに適用される frontmatter の共通仕様と、wikilinkに意味を持たせるための `relations` / `type` 辞書を定義する。

---

## 1. 共通フィールド（すべてのノート）

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `type` | string | ✅ | `person` / `episode` / `insight` / `law` / `guideline` / `framework` / `disorder` / `method` / `assessment` / `service` / `org` / `stakeholder` / `care-role` / `substitute` / `simulation` / `moc` / `layer-readme` / `meta` |
| `id` | string | 層依存 | 仮名ID（P-XXXX 等）。知識層は不要 |
| `tags` | array | ✅ | Obsidianタグ |
| `cssclasses` | array | 推奨 | 層別配色用。後述の対応表を参照 |
| `created` | date | 推奨 | 作成日 |
| `updated` | date | ✅ | 最終更新日 |
| `review_due` | date | 層依存 | 次回見直し期限（法令・ガイドライン・サービスは必須） |
| `relations` | array | 推奨 | 重み付きリンク（後述） |

### 1.1 cssclasses 対応表（彩色システム）

`.obsidian/snippets/layer-colors.css` を有効化すると、以下の `cssclasses` 値でリーディングビューのタイトルにカラーアクセントが付く。グラフビューはパスベースで自動彩色（`.obsidian/graph.json`）。

| 層 | cssclasses 値 | 色 |
|---|---|---|
| 60_Laws | `layer-law` | 🟥 Red |
| 61_Guidelines | `layer-guideline` | 🟧 Orange |
| 62_Frameworks | `layer-framework` | 🟪 Purple |
| 63_Disorders | `layer-disorder` | 🟨 Amber |
| 64_Methods | `layer-method` | 🟩 Green |
| 65_Assessments | `layer-assessment` | 🟫 Brown |
| 66_Services | `layer-service` | 🟦 Blue |
| 67_Orgs | `layer-org` | 🟦 Teal |
| 10_People | `layer-person` | ⚫ Blue-Gray |
| 00_MOC | `layer-moc` | ⭐ Gold |

例:

```yaml
---
type: law
cssclasses: [layer-law]
tags: [law]
---
```

---

## 2. 層別の追加フィールド

### 2.1 `law`（60_Laws/）
```yaml
type: law
law_name: "障害者総合支援法"        # 必須
short_name: "総合支援法"           # 必須（wikilink略称）
source_url: "https://..."         # 必須（e-Gov等）
version: "令和6年改正"             # 必須
effective_date: 2024-04-01        # 必須
review_due: 2027-04-01            # 必須（次回改正予定）
issuer: "厚生労働省"               # 必須
articles_covered: ["5条", "77条"]  # 任意
```

### 2.2 `guideline`（61_Guidelines/）
```yaml
type: guideline
guideline_name: "意思決定支援ガイドライン"  # 必須
issuer: "厚生労働省"                      # 必須
source_url: "https://..."                # 必須
version: "平成29年3月策定"                # 必須
effective_date: 2017-03-31              # 必須
review_due: 2027-03-31                  # 必須
related_laws: ["[[障害者総合支援法]]"]     # 推奨
```

### 2.3 `framework`（62_Frameworks/）
```yaml
type: framework
framework_name: "ICF"
origin: "WHO"                     # 必須
year: 2001                        # 必須
domain: ["医療", "福祉", "教育"]    # 必須
source_url: ""
```

### 2.4 `disorder`（63_Disorders/）
```yaml
type: disorder
disorder_name: "自閉スペクトラム症"
icd11_code: "6A02"                # 必須（該当あれば）
dsm5_code: "299.00"               # 必須（該当あれば）
prevalence: "約1-2%"               # 推奨
onset_typical: "乳幼児期"           # 推奨
```

### 2.5 `method`（64_Methods/）
```yaml
type: method
method_name: "構造化支援"
evidence_level: high              # 必須: high | moderate | low | emerging
target_disorder: ["[[自閉スペクトラム症]]"]  # 必須
training_required: true           # 必須
underpinned_by: ["[[TEACCH]]"]    # 推奨
```

### 2.6 `assessment`（65_Assessments/）
```yaml
type: assessment
assessment_name: "障害支援区分認定調査"
administrator: "市町村認定調査員"   # 必須
time_required: "60-90分"           # 必須
purpose: "サービス支給量の決定"     # 必須
items: 80                          # 任意
```

### 2.7 `service`（66_Services/）
```yaml
type: service
service_name: "行動援護"
law_basis: "[[障害者総合支援法]]"   # 必須
target: "障害支援区分3以上+行動関連項目10点以上"  # 必須
fee_code: "115"                    # 任意
duration: "原則1年"                 # 任意
version: "令和6年度報酬改定"         # 必須
review_due: 2027-04-01             # 必須
```

### 2.8 `org`（67_Orgs/）
```yaml
type: org
org_type: "基幹相談支援センター"
role: "地域の相談支援体制の中核"     # 必須
mandate: "[[障害者総合支援法]] 77条の2"  # 必須
referral_routes: ["市町村障害福祉課"]  # 推奨
```

### 2.9 `person`（10_People/ — 既存テンプレ参照）
既存の `90_Meta/templates/person.md` を踏襲。

---

## 3. relations — 重み付きリンク

wikilinkに「意味」と「強さ」を持たせるための構造化配列。

### 3.1 基本スキーマ

```yaml
relations:
  - to: "[[障害者総合支援法]]"         # 必須: wikilink形式
    type: applies-to                # 必須: 下記辞書参照
    weight: 0.9                     # 必須: 0.0-1.0
    evidence: "区分5+行動関連10点"    # 推奨: 重みの根拠
    rationale: ""                    # 任意: 補足説明
    source: "[[アセスメント記録2026-03]]"  # 任意: 根拠ノート
    updated: 2026-04-20              # 推奨
    condition: ""                    # 任意: 条件付きリンク
```

### 3.2 weight の基準

| 範囲 | 意味 |
|---|---|
| 0.95-1.00 | 法的義務／絶対的禁忌 |
| 0.80-0.94 | 強い推奨／強い適合 |
| 0.60-0.79 | 推奨／該当可能性高い |
| 0.40-0.59 | 検討に値する／弱い示唆 |
| 0.20-0.39 | 可能性低い／参考情報 |
| 0.00-0.19 | ほぼ該当なし（記録のみ） |

---

## 4. リンク型辞書（type）

リンクに **方向性** と **意味** を持たせる。

### 4.1 法令・コンプライアンス系
| type | 方向 | 意味 | 使用例 |
|---|---|---|---|
| `applies-to` | 法令→対象 | 法令が対象に適用される | [[総合支援法]] applies-to P-0001 |
| `mandated-by` | 機関/サービス→法令 | 法令が根拠となる | [[基幹相談]] mandated-by [[総合支援法]] |
| `mandatory-report-trigger` | ガイドライン→利用者 | 通報義務の引き金 | [[虐待防止法]] → P-0001 |
| `compliance-required` | 対象→ガイドライン | 記録/運用義務がある | P-0001 compliance-required [[身体拘束適正化の手引]] |

### 4.2 サービス適格系
| type | 方向 | 意味 |
|---|---|---|
| `eligible-service` | 利用者→サービス | 受給資格がある |
| `currently-using` | 利用者→サービス | 現在利用中 |
| `considered` | 利用者→サービス | 検討中 |
| `discontinued` | 利用者→サービス | 利用終了 |
| `supersedes-at` | サービス→サービス | 他制度への切替（例：介護保険65歳） |
| `provided-by` | サービス→機関 | 提供主体 |
| `delivers` | 機関→サービス | 機関が提供するサービス |

### 4.3 障害・技法系
| type | 方向 | 意味 |
|---|---|---|
| `has-characteristic` | 利用者→障害 | 該当する障害特性 |
| `comorbid-with` | 障害↔障害 | 併存関係 |
| `responds-to` | 障害→技法 | 適応技法 |
| `contraindicated` | 障害→技法 | 禁忌技法 |
| `recommended` | 利用者→技法 | 推奨される技法 |
| `evidence-based` | 利用者→技法 | エビデンス支持あり |
| `underpinned-by` | 技法→理論 | 理論的裏付け |
| `informs` | 理論→技法 | 理論が技法を導く |

### 4.4 関係・連携系
| type | 方向 | 意味 |
|---|---|---|
| `escalate-to` | 利用者→機関 | 危機時の連携先 |
| `instance-of` | 具体→類型 | 具体事業所↔機関類型 |
| `referred-by` | 利用者→機関 | 紹介元 |
| `supports` | 支援者→利用者 | 支援関係 |

### 4.5 メタ関係
| type | 方向 | 意味 |
|---|---|---|
| `contradicts` | A↔B | 矛盾・対立 |
| `complements` | A↔B | 相補的 |
| `supersedes` | 新→旧 | 代替・廃止 |
| `derived-from` | 派生→元 | 派生関係 |

---

## 5. エピソード・インサイトとの接続

既存の `20_Episodes/` / `30_Insights/` は、新設の知識層（60-67）を **出典** として参照できる:

```yaml
# 30_Insights/panic-pattern-P0001.md
type: insight
relations:
  - to: "[[64_Methods/構造化支援]]"
    type: underpinned-by
    weight: 0.8
  - to: "[[63_Disorders/自閉スペクトラム症]]"
    type: explains
    weight: 0.7
```

これで「現場の観察 → 理論的裏付け → 支援技法」の鎖がグラフ上でトラバース可能になる。

---

## 6. バリデーション（将来）

以下は `data-quality-agent` で定期監視予定:

- [x] 必須フィールドの欠損検出
- [x] `review_due` 期限超過の検出
- [x] `weight` 値の範囲逸脱（0.0-1.0 外）
- [x] `to` wikilinkの壊れ検出
- [x] 孤児ノート（誰からも参照されていない）の検出
- [x] `type` 辞書外の使用検出

---

## 7. 変更履歴

- 2026-04-20: 初版（F1骨組み）
