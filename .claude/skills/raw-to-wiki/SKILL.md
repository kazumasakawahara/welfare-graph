---
name: raw-to-wiki
description: raw/ フォルダに置かれた一次資料（PDF・MD・テキスト・Web 等）を読み、適切な層（60_Laws / 61_Guidelines / 62_Frameworks / 63_Disorders / 64_Methods / 65_Assessments / 66_Services / 67_Orgs / 30_Insights）のテンプレートに沿った wiki ページを生成する。frontmatter の必須フィールドを自動で埋め、本文を要約・構造化し、既存ページとの relations を提案する。
---

<!-- allow-realname -->

# raw-to-wiki skill

## 🪷 合言葉（事前自問）

> **「いつか必要」は「今は不要」と同義**

ingest を始める前に必ず自問する。詳細な判断基準は [[90_Meta/page-creation-principles]] §2 の 3 関門（Q1 今日の実務で助かったか／Q2 raw/ に原典があるか／Q3 作らなかったら誰がいつ困るか）を通すこと。**投機的な ingest は禁止**。

## 用途

raw/ に置かれた一次資料を、wiki の適切な層に **要約・構造化された ノート** として取り込む。

### 取り込みの主なケース

- **法令の改正**: e-Gov の最新 PDF を `raw/laws/` に → `60_Laws/` を更新
- **新ガイドライン**: 厚労省 PDF を `raw/guidelines/` に → `61_Guidelines/` に新規作成
- **判例・事件**: Wikipedia 記事や判決文を `raw/insights/` に → `30_Insights/` に取り込み
- **報酬告示**: `raw/services/` に → `66_Services/` を更新
- **学会報告**: `raw/reports/` に → `30_Insights/` または `90_Meta/` に

## 入力

- raw/ 内のファイルパス（必須）
- 取り込み先層（任意・自動判定可能）
- 取り込み先ファイル名（任意・自動推定可能）

## 出力フォーマット

取り込み先ファイル（`60_Laws/xxx.md` など）に以下の構造で書き込む:

```markdown
<!-- allow-realname -->
---
type: {law / guideline / framework / disorder / method / assessment / service / org / insight}
{各層の必須 frontmatter}
source: "raw/{subfolder}/{filename}"
cssclasses: [layer-{type}]
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tags: [{適切なタグ}]
relations:
  - to: "[[既存ページ]]"
    type: {applies-to / complements / informs / ...}
    weight: {0.0-1.0}
    rationale: "{なぜこの関係があるか}"
---

# {タイトル}

## 概要
（1-3 段落で要旨）

## {内容に応じた章立て}
...

## 出典
- raw/ 元ファイル: `raw/{subfolder}/{filename}`
- 一次情報: {URL or 書籍 ISBN}
```

## 実行手順（Claude 向け）

### 1. raw/ ファイルを読む

ファイル形式により異なる:

- **`.md` / `.txt`**: Read ツールでそのまま読込
- **`.pdf`**: Read ツールに `pages` 引数で範囲指定可能
- **`.docx`**: 必要に応じて Bash で `pandoc` 等で md 化
- **URL**: WebFetch で取得

### 2. 内容を分析し、層を判定

ファイル内容と raw/ サブフォルダから取り込み先層を推定:

| raw/ サブフォルダ | デフォルト層 | 例外（内容で判断） |
|---|---|---|
| `raw/laws/` | `60_Laws/` | 通知・告示なら `61_Guidelines/` |
| `raw/guidelines/` | `61_Guidelines/` | サービス報酬なら `66_Services/` |
| `raw/services/` | `66_Services/` | — |
| `raw/insights/` | `30_Insights/` | 学術的な理論なら `62_Frameworks/` |
| `raw/reports/` | `30_Insights/` | 統計データなら `90_Meta/` |

複数層に跨る場合は **主たる層** に取り込み、関連層に relations を張る。

### 3. ファイル名・タイトルを決定

- 既存 wiki ページと **重複しない** 命名
- 検索しやすい日本語名（例: `七生養護学校事件_性教育とバックラッシュ.md`）
- 法令・サービスは正式名（例: `障害者総合支援法.md`）

### 4. テンプレートを選択し frontmatter を生成

`90_Meta/templates/{type}.md` を参考に必須フィールドを埋める:

#### 共通必須
- `type`: 層に対応する type
- `created`: 今日
- `updated`: 今日
- `tags`: 適切なタグ配列
- `cssclasses: [layer-{type}]`

#### 層別必須（[[90_Meta/SCHEMA]] 参照）
- **law**: source_url, version, effective_date, review_due, issuer
- **guideline**: issuer, source_url, version, effective_date, review_due
- **service**: law_basis, target, version, review_due
- **framework**: origin, year, domain
- **disorder**: icd11_code または dsm5_code
- **method**: evidence_level, target_disorder
- **assessment**: administrator, time_required, purpose
- **org**: role, mandate
- **insight**: applies_to_disorders, applies_to_methods, evidence_level

#### 追加（取り込み元情報）
- `source`: raw/ への相対パス
- 元の raw ファイルが残ることで、後で原文確認が可能

### 5. 本文を要約・構造化

#### 要約の方針

- A4 1-2 ページ程度（2000-4000 文字）を目安
- 一次情報の構造を保ちつつ、相談支援業務での使い方を明確に
- 章立てはテンプレートに沿うが、内容に応じて調整可

#### 必ず含める章

- **概要**: 1-3 段落で要旨
- **計画相談での論点 / 活用** または **相談支援との関係**
- **関連法令 / ガイドライン / 技法 等**（既存ページへの wikilink）
- **出典**: raw/ 元ファイル + 一次情報 URL

#### 章立て例（事件・判例の場合）

```
## 概要
## 事件の経緯
## 裁判の結果
## 計画相談支援との関係
## 関連する制度・概念の変化
## 関連ページ
## 参考文献・出典
```

### 6. relations を提案

raw/ の内容を分析し、既存 wiki ページとの関係を 3-10 個提案:

```yaml
relations:
  - to: "[[64_Methods/知的障害のある人への性教育]]"
    type: complements
    weight: 0.9
    rationale: "本事件は知的障害児向け性教育の実践事例"
  - to: "[[62_Frameworks/包括的性教育]]"
    type: informs
    weight: 0.8
  - to: "[[60_Laws/旧優生保護法]]"
    type: complements
    weight: 0.7
    rationale: "障害者の性に対する社会の認識史の文脈"
```

### 7. 実名混入チェック

raw/ に実在の氏名が含まれている場合の処理:

- **公人**（議員・首長・公報情報）: 引用 OK（`<!-- allow-realname -->` を付与）
- **当事者**（生徒・利用者・職員）: **役割で表現** に置換
  - 「校長 X」→「元校長」
  - 「教員 Y」→「原告教員」
  - 「生徒 Z」→「在校生」

判決文の当事者名は基本的に役割表現で記述。

### 8. ユーザーに確認

書き込み前に、以下をユーザーに提示し承認を得る:

```
取り込み先: 30_Insights/七生養護学校事件_性教育とバックラッシュ.md
推定 type: insight
relations 候補: 7 個（[[64_Methods/...]] 等）

本文の書き出し:
> 七生養護学校事件は、2003年に東京都立七生養護学校で行われていた
> 知的障害児への性教育「こころとからだの学習」が...

このまま保存してよいですか？
```

### 9. 書き込み

承認後、Write ツールで書き込み。
書き込み後、以下を実施:

- 既存ページにも back-link を追加（任意・推奨）
- vault-health-check の「壊れリンク」が増えていないか確認

### 10. 完了報告

ユーザーに以下を報告:

```
✅ 取り込み完了

新規ページ: 30_Insights/七生養護学校事件_性教育とバックラッシュ.md
relations: 7 個
要約: A4 約 2 ページ
出典: raw/insights/2003_七生養護学校事件.md（原本保管）

次のステップ:
- Obsidian で開いて内容確認
- 必要に応じて手修正
- Neo4j に再同期: python3 90_Meta/scripts/sync_to_neo4j.py
```

## 禁忌・注意事項

### 取り込んではいけないケース

- **原本に著作権上の問題がある**（PDF 全文転載等）→ 引用範囲内の要約に限定
- **個人情報を含む生データ**（実在の利用者情報）→ 仮名化してから取り込み

### 一次情報の改変禁止

- raw/ の元ファイルは **絶対に改変しない**（原本として保管）
- 取り込み後の wiki ページが「要約」であることを明示

### 実名の取扱い

- ノート本文中の **当事者名は役割表現に置換**
- frontmatter の `source` で raw/ 原本へのリンクを残し、必要時に原文参照可

### 既存ページの上書き

- 同名の既存ページがある場合、**ユーザーに確認** してから上書き
- 古い版は git 履歴で残るので、慎重に判断

### 著作権配慮（公開リポジトリ）

- 法令の原文 PDF は `.gitignore` で除外済み
- ガイドライン・告示の原本も基本的にローカル保管
- wiki ページ側には **要約と出典 URL のみ**（全文転載しない）

## 引用範囲の目安

著作権法 32 条に基づく適法な引用:

- ✅ 原文の **数行〜数段落** を「」付きで引用、出典明示
- ✅ 全体の構造を **要約** で示す
- ❌ 原文の **大部分**（数ページ）をそのまま転記
- ❌ 元の表現の **改変なき転載** が大きな割合を占める

迷う場合は要約寄りに判断。

## 関連スキル

- `vault-health-check`: 取り込み後の健全性確認
- `support-hypothesis`: 取り込んだ知識を利用者ノートで活用
- `wiki-ingest`（外部・anthropic-skills）: 類似機能の汎用版
- `wiki-integrate`（外部）: 既存 wiki への統合特化

## 関連ドキュメント

- [[raw/README]]: raw/ 全体の運用ルール
- [[90_Meta/SCHEMA]]: frontmatter 仕様・リンク型辞書
- [[docs/USER_GUIDE]]: ユーザー向け取り込み手順

## 将来拡張

- **OCR 対応**: スキャン PDF からのテキスト抽出
- **Word 文書対応**: pandoc 経由での変換
- **動画書き起こし**: 研修動画→テキスト→wiki
- **バッチ取り込み**: raw/ の複数ファイルを一括処理
- **差分取り込み**: 既存ページの法改正反映（diff 表示・部分更新）
