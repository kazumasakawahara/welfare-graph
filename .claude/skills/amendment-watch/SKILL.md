---
name: amendment-watch
description: 法令・ガイドライン・サービス報酬の改正情報を監視し、welfare-graph の該当ノートに反映が必要かどうかを評価する。review_due 期限、version_hash ドリフト、一次ソース（e-Gov / 厚労省 / 官報）の新着告知を巡回し、改正予告があれば status を pending-amendment に変更する提案を行う。月次定期実行または告知受領時に使用。
---

<!-- allow-realname -->

# amendment-watch skill

## 用途

welfare-graph を **進化する知識グラフ** として維持するために、法制度の改正動向を定期監視する。検知したら該当ノートの `status` を更新し、相談支援専門員に「要確認リスト」を提示する。

## 入力

- 対象範囲（任意）: `all` / `60_Laws` / `61_Guidelines` / `66_Services` / `指定ノートのパス`
  - デフォルト: `all`
- モード（任意）: `check` / `update-status` / `integrate`
  - `check`: 検知のみ（デフォルト）
  - `update-status`: 検知後に status を pending-amendment に更新
  - `integrate`: さらに raw/ 配下に配置済みの原文で差分取込を試みる

## 出力フォーマット

```markdown
# 改正追随監視結果 {YYYY-MM-DD}

## 🚨 要対応（改正告知・施行日変更あり）
- [[60_Laws/障害者総合支援法]]
  - 検知: e-Gov 新着に「令和9年改正案」掲載（source: {URL}）
  - 推奨: status → pending-amendment、review_due → 2027-04-01 前倒し

## ⚠️ 期限近接（3 か月以内）
- [[66_Services/就労継続支援B型]]: review_due 残り 45 日

## 📋 version_hash ドリフト検知
- [[61_Guidelines/意思決定支援ガイドライン]]
  - 保存: a3b4c5d6
  - 現在: f7e8d9c0
  - 一次ソース更新の可能性あり

## 📊 統計
- 監視対象: 37 ノート
- 改正告知: 1 件
- 期限近接: 3 件
- ドリフト: 1 件
```

## 実行手順（Claude 向け）

### ステップ 1: 検知層の実行

```bash
/usr/bin/python3 90_Meta/scripts/amendment_check.py
```

または、オンライン検証を含む場合:

```bash
/usr/bin/python3 90_Meta/scripts/amendment_check.py --online
```

結果は `90_Meta/amendment-reports/{YYYY-MM-DD}.md` に保存される。

### ステップ 2: 一次ソース巡回（オプション）

以下のフィードをチェック（WebFetch 可能な場合）:

| 対象 | URL |
|---|---|
| e-Gov 法令新着 | https://laws.e-gov.go.jp/ |
| 厚労省 障害保健福祉部 新着 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/shougaishahukushi/index.html |
| 内閣府 障害者施策 | https://www8.cao.go.jp/shougai/ |
| 官報（政府刊行） | https://kanpou.npb.go.jp/ |

改正関連のキーワードを検出:
- 「改正」「一部改正」「全部改正」
- 「施行日」「政令」「省令」
- 「新設」「廃止」「経過措置」

### ステップ 3: 該当ノートの評価

各検知項目について、対応するノートの frontmatter をレビュー:

1. `status` が `active` → `pending-amendment` に変更提案
2. `review_due` を改正予告日に合わせて前倒し
3. `last_verified` を更新
4. 改正概要を `amendment_history` にドラフト追加

### ステップ 4: ユーザー確認

提案内容を提示し、承認を得てから以下を実行:

- frontmatter の更新
- `00_MOC/Home.md` に改正予告バナーを追加
- 関連する利用者ノート（10_People/）にインパクト通知（高 weight relations のみ）

### ステップ 5: モード別追加処理

**update-status モード**: ステップ 4 までを一括承認で実行

**integrate モード**: さらに以下を実行
- `raw/laws/` に原文 PDF/テキストが存在するか確認
- 存在すれば `law-amendment-integrate` スキルに処理を引き継ぎ
- 存在しなければ「原文取得待ち」として記録

## 自動化パターン

### GitHub Actions 月次実行

`.github/workflows/amendment-check.yml`:

```yaml
name: amendment-check
on:
  schedule:
    - cron: '0 0 1 * *'  # 毎月 1 日 00:00 UTC
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install python-frontmatter
      - run: python 90_Meta/scripts/amendment_check.py --online
      - name: Commit report
        run: |
          git config user.name "amendment-bot"
          git config user.email "amendment-bot@users.noreply.github.com"
          git add 90_Meta/amendment-reports/
          git commit -m "chore: monthly amendment check $(date +%Y-%m)" || exit 0
          git push
      - name: Create Issue if CRITICAL
        if: ${{ ... }}
        uses: peter-evans/create-issue-from-file@v5
        with:
          title: "改正追随: ${{ env.DATE }} 緊急対応項目"
          content-filepath: 90_Meta/amendment-reports/${{ env.DATE }}.md
```

### ローカル定期実行（cron）

```bash
# 毎月 1 日 9:00 に実行
0 9 1 * * cd /path/to/welfare-graph && /usr/bin/python3 90_Meta/scripts/amendment_check.py --online
```

## 注意事項

- **一次ソース絶対主義**: ブログや二次情報は参考扱い、官公庁サイトのみを根拠に
- **過剰反応禁止**: ハッシュドリフトだけで自動更新しない（手動確認必須）
- **実名混入チェック**: 改正情報取得時に個人名が含まれていないか確認
- **誤検知受容**: e-Gov の PDF 配信形式変更等でハッシュが変わることあり → `last_verified` の更新で対応
- **版跨ぎ関係**: 経過措置期間中は旧版と新版が併存しうる → `condition` フィールドで明記

## 関連スキル

- [[law-amendment-integrate]]: 改正差分を実際にノートに取り込む
- [[raw-to-wiki]]: 改正原文を raw/laws/ から wiki ページ化
- [[vault-health-check]]: 全体的な品質チェック（改正追随も含む）
