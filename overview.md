<!-- allow-realname -->
---
type: meta
updated: 2026-04-21
tags: [meta, overview]
cssclasses: [layer-meta]
---

# welfare-graph 俯瞰ダッシュボード

**最終更新**: 2026-04-21（`generate_overview.py` により自動生成）

本ファイルは [[CLAUDE#§3 動作モード（5 + 2）]] の overview モード出力。
手動編集は行わず、`python3 90_Meta/scripts/generate_overview.py` で再生成すること。

---

## 📊 全体サマリ

- **総ノート数**: 121
- **総 relations**: 355
- **平均 relations/ノート**: 2.9

## 🗂 層別ページ数

| 層 | 件数 |
|---|---|
| 00_MOC | 7 |
| 10_People | 3 |
| 30_Insights | 6 |
| 50_Resilience | 2 |
| 60_Laws | 11 |
| 61_Guidelines | 11 |
| 62_Frameworks | 7 |
| 63_Disorders | 12 |
| 64_Methods | 13 |
| 65_Assessments | 9 |
| 66_Services | 21 |
| 67_Orgs | 13 |
| 90_Meta | 6 |

## 📑 type 別ページ数

| type | 件数 |
|---|---|
| service | 20 |
| org | 12 |
| method | 12 |
| disorder | 11 |
| guideline | 10 |
| law | 10 |
| layer-readme | 8 |
| moc | 7 |
| assessment | 7 |
| meta | 6 |
| insight | 6 |
| framework | 6 |
| person | 3 |
| care_role | 1 |
| substitute | 1 |

## 🔄 status 別ページ数

| status | 件数 |
|---|---|
| active | 119 |
| archived | 1 |
| 検討中 | 1 |

## 🚨 改正追随状況

- pending-amendment（改正予告中）: 0 件
- review_due 超過: 0 件
- 3 か月以内に review_due: 0 件

## 🔗 被参照ノート Top 15

| 順位 | ノート | 被参照数 |
|---|---|---|
| 1 | [[60_Laws/障害者総合支援法]] | 36 |
| 2 | [[63_Disorders/自閉スペクトラム症]] | 19 |
| 3 | [[63_Disorders/知的障害]] | 17 |
| 4 | [[63_Disorders/強度行動障害]] | 13 |
| 5 | [[60_Laws/障害者虐待防止法]] | 12 |
| 6 | [[61_Guidelines/意思決定支援ガイドライン]] | 11 |
| 7 | [[60_Laws/発達障害者支援法]] | 8 |
| 8 | [[60_Laws/精神保健福祉法]] | 8 |
| 9 | [[64_Methods/構造化支援]] | 7 |
| 10 | [[62_Frameworks/ICF]] | 7 |
| 11 | [[63_Disorders/統合失調症]] | 7 |
| 12 | [[64_Methods/ABC分析]] | 7 |
| 13 | [[66_Services/計画相談支援]] | 7 |
| 14 | [[66_Services/精神通院医療]] | 7 |
| 15 | [[64_Methods/強度行動障害支援]] | 6 |

## 📅 最近の変更（git log 直近 15 件）

| commit | date | message |
|---|---|---|
| `ac4ba82` | 2026-04-20 | feat(mcp): welfare-graph MCP サーバーを実装 — Claude Desktop / Code から照会可能に |
| `366ba78` | 2026-04-20 | feat: 進化する知識グラフ機構 — 法令改正追随システムを実装 |
| `c4b1d5f` | 2026-04-20 | feat: raw → wiki 取り込みワークフローと七生養護学校事件の取り込み |
| `6576e2d` | 2026-04-20 | docs: 相談支援専門員向けの使用説明書を追加 |
| `6b4199f` | 2026-04-20 | 初期公開: welfare-graph — 相談支援専門員のための知識グラフ |
| `9e9053e` | 2026-04-20 | Initial commit |

## 🕸 層間関係グラフ（Mermaid）

relations が 3 件以上ある層間接続を表示。数字は接続数。

```mermaid
graph LR
    00MOC["00_MOC<br/>(7)"]
    10People["10_People<br/>(3)"]
    30Insights["30_Insights<br/>(6)"]
    50Resilience["50_Resilience<br/>(2)"]
    60Laws["60_Laws<br/>(11)"]
    61Guidelines["61_Guidelines<br/>(11)"]
    62Frameworks["62_Frameworks<br/>(7)"]
    63Disorders["63_Disorders<br/>(12)"]
    64Methods["64_Methods<br/>(13)"]
    65Assessments["65_Assessments<br/>(9)"]
    66Services["66_Services<br/>(21)"]
    67Orgs["67_Orgs<br/>(13)"]
    90Meta["90_Meta<br/>(6)"]
    66Services -->|23| 60Laws
    64Methods -->|19| 63Disorders
    67Orgs -->|14| 60Laws
    63Disorders -->|14| 64Methods
    63Disorders -->|13| 66Services
    10People -->|13| 66Services
    61Guidelines -->|12| 60Laws
    66Services -->|11| 63Disorders
    10People -->|10| 64Methods
    10People -->|9| 63Disorders
    10People -->|9| 62Frameworks
    10People -->|9| 61Guidelines
    61Guidelines -->|7| 66Services
    63Disorders -->|7| 60Laws
    60Laws -->|7| 63Disorders
    10People -->|7| 60Laws
    10People -->|7| 67Orgs
    67Orgs -->|6| 66Services
    66Services -->|6| 67Orgs
    30Insights -->|5| 64Methods
    61Guidelines -->|5| 64Methods
    60Laws -->|5| 67Orgs
    10People -->|5| 65Assessments
    30Insights -->|4| 62Frameworks
    67Orgs -->|4| 63Disorders
    66Services -->|4| 61Guidelines
    60Laws -->|4| 61Guidelines
    60Laws -->|4| 66Services
    62Frameworks -->|4| 60Laws
    65Assessments -->|4| 62Frameworks
    65Assessments -->|4| 63Disorders
    30Insights -->|3| 63Disorders
    30Insights -->|3| 66Services
    62Frameworks -->|3| 61Guidelines
    65Assessments -->|3| 66Services
    64Methods -->|3| 61Guidelines
```

---

## 🔧 再生成

```bash
python3 90_Meta/scripts/generate_overview.py
```

関連: [[CLAUDE]] / [[90_Meta/SCHEMA]] / [[90_Meta/amendment-tracking]] / [[README]]