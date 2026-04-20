<!-- allow-realname -->
# raw/ — 一次資料保管庫

このフォルダは、wiki に取り込む前の **一次資料・原稿** の置き場です。

ここに置いたファイルは **wiki にそのままは反映されません**。`raw-to-wiki` スキル
（または手作業）で要約・構造化して、適切な層（60_Laws / 61_Guidelines / ...）に
配置されることで wiki の一部となります。

## 📂 サブフォルダ構成

| フォルダ | 取り込み先層 | 例 |
|---|---|---|
| `raw/laws/` | `60_Laws/` | e-Gov の法令 PDF・条文集 |
| `raw/guidelines/` | `61_Guidelines/` | 厚労省ガイドライン PDF・通知 |
| `raw/services/` | `66_Services/` | 報酬告示・サービス通知 |
| `raw/insights/` | `30_Insights/` | 判例・事例・ナラティブ・Wikipedia 記事 |
| `raw/reports/` | `30_Insights/` または `90_Meta/` | 学会発表・調査報告書 |

その他の取り込み先層（`62_Frameworks/`・`63_Disorders/`・`64_Methods/`・
`65_Assessments/`・`67_Orgs/`）は、内容に応じて `raw/insights/` や
`raw/reports/` から取り込んでください。

## 📄 受け付けるファイル形式

| 形式 | 拡張子 | 備考 |
|---|---|---|
| PDF | `.pdf` | 法令・ガイドライン原本 |
| Markdown | `.md` | Wikipedia 記事・既存メモ |
| プレーンテキスト | `.txt` | 書き起こし・メール |
| Word | `.docx` | 報告書（読込にツール要） |
| Web ページ | URL | `firecrawl-scrape` 等で取得 |

## 🚀 取り込み手順

### 方法 A: Claude Code で自動取り込み（推奨）

1. raw/ の適切なサブフォルダに資料を配置
2. Claude Code で以下を実行:
   ```
   raw/insights/七生養護学校事件.md を wiki に取り込んで
   ```
3. Claude が `raw-to-wiki` スキル相当の処理を行い、
   - 適切な層・テンプレートを判定
   - frontmatter を自動生成
   - 本文を要約・構造化
   - 既存ページとの relations を提案
4. 確認 → 保存

詳細手順は [docs/USER_GUIDE.md](../docs/USER_GUIDE.md#raw資料の取り込み) 参照。

### 方法 B: 手作業で取り込み（Claude を使わない場合）

1. raw/ の資料を Obsidian で開く（または別のビューアで読む）
2. 取り込み先の層のテンプレートをコピー（`90_Meta/templates/{type}.md`）
3. 内容を要約して新しいノートを作成
4. frontmatter の必須フィールドを埋める（`source_url`・`version`・`review_due` 等）
5. 既存ページに wikilink で繋げる
6. raw/ の元ファイルを参照として残す（パスを本文末尾に）

## ⚠️ 注意事項

### 著作権配慮

- **法令・通知の原文 PDF は git に含めない**（`.gitignore` で除外済み）
- ローカルでのみ保管・参照
- 公開リポジトリには **要約・出典 URL のみ** を載せる

### 実名混入防止

- raw/ 内の資料に実在の氏名が含まれている場合（例: 判決文の当事者名）、
  取り込み時に **役割で表現**（「原告教員」「被告都教委」等）に置き換える
- 公人（議員・首長等）の氏名は文脈次第で残してよい
  → 公開議員発言・公報情報は引用 OK

### 一次情報の改変禁止

- raw/ の元ファイルは **改変しない**（原本として保管）
- 要約は wiki ページ側で行い、原本へのパス（`source` フィールド）で参照可能にする

## 📝 命名規則

### 法令・ガイドライン
```
raw/laws/{法令略称}_{版名}.pdf
例: raw/laws/障害者総合支援法_令和6年改正.pdf
```

### 事例・判例
```
raw/insights/{年月}_{事件名・事例名}.{ext}
例: raw/insights/2003_七生養護学校事件.md
```

### 報告書
```
raw/reports/{年月}_{発行元}_{タイトル略}.pdf
例: raw/reports/2024-07_最高裁_旧優生保護法違憲判決.pdf
```

## 🔍 取り込み済みかの確認

raw/ のファイルが wiki 化されたかを確認するには、対応する層で検索:

```
[Obsidian] Cmd+Shift+F で全文検索
キーワード: source: "raw/insights/2003_七生養護学校事件"
```

これでヒットしたページが、その raw 資料から派生した wiki ページです。
