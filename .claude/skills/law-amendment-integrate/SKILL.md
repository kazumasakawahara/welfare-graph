---
name: law-amendment-integrate
description: 法令・ガイドライン・サービス報酬の改正差分を welfare-graph に取り込む。旧版を archived/ に退避し、新版で現行ノートを更新し、影響を受ける relations を再評価する。raw/laws/ などに配置された原文を起点に、Neo4j で波及範囲を算出し、利用者ノートへのインパクトを通知する。改正施行時に使用。
---

<!-- allow-realname -->

# law-amendment-integrate skill

## 用途

法改正・ガイドライン更新・報酬改定が施行された際、welfare-graph 全体を整合性を保ったまま更新する。単なるテキスト置換ではなく、**版管理 + 差分記録 + 波及分析 + relations 再評価** を一体で実施する。

## 入力（必須）

- 対象ノート: 例 `60_Laws/障害者総合支援法.md`
- 原文ソース: 例 `raw/laws/障害者総合支援法_令和9年改正.pdf`
- 新版情報:
  - `version`: 例「令和9年改正」
  - `effective_date`: 例 `2027-04-01`
  - `summary`: 改正の概要（1-3 行）

## 処理フロー

```
[入力確認] → [旧版アーカイブ] → [新版反映] → [波及分析] → [relations 再評価] → [承認]
```

### ステップ 1: 入力確認

1. 対象ノートを Read し、現在の frontmatter を取得
2. `version`, `effective_date`, `amendment_history` を確認
3. 原文ファイルの存在確認（PDF / MD / テキスト）
4. ユーザーに計画を提示:
   ```
   【改正取込プラン】
   対象: 60_Laws/障害者総合支援法.md
   現行版: 令和6年改正 (effective: 2024-04-01)
   新版: 令和9年改正 (effective: 2027-04-01)
   原文: raw/laws/障害者総合支援法_令和9年改正.pdf
   影響波及予測: ... ノート（次ステップで算出）
   ```

### ステップ 2: 旧版アーカイブ

1. `60_Laws/archived/` フォルダがなければ作成
2. 現行ノートを複製: `60_Laws/archived/{法令名}_{現行版}.md`
3. 複製ノートの frontmatter を更新:
   ```yaml
   status: archived
   superseded_by: "[[60_Laws/障害者総合支援法]]"
   effective_date_end: 2027-03-31   # 新版施行前日
   ```
4. 本文冒頭に注記追加:
   ```markdown
   > ⚠️ このページは旧版（令和6年改正）です。
   > 現行版: [[60_Laws/障害者総合支援法]]
   > 旧版の内容は歴史的参照のために保存されています。
   ```

### ステップ 3: 新版反映

1. 原文（PDF/MD）を読み取り、改正点を抽出:
   - 条文の追加・削除・変更
   - 新設サービス / 廃止サービス
   - 新しい義務・権利
2. 現行ノートを更新:
   - `version`, `effective_date`, `review_due`, `last_verified` を新版値に
   - `version_hash` を新しい原文ハッシュに
   - `amendment_history` に新エントリ追加:
     ```yaml
     amendment_history:
       - version: "令和6年改正"
         effective_date: 2024-04-01
         summary: "..."
         archived_as: "[[archived/障害者総合支援法_R6]]"
       - version: "令和9年改正"
         effective_date: 2027-04-01
         summary: "障害支援区分の再編、就労系サービス統合"
         archived_as: "[[archived/障害者総合支援法_R6]]"
         diff_source: "[[raw/laws/障害者総合支援法_令和9年改正.pdf]]"
     ```
   - `supersedes: "[[60_Laws/archived/障害者総合支援法_R6]]"`
   - `status: active`
3. 本文を改正内容に合わせて更新（要約・サービス一覧など）

### ステップ 4: 波及分析

Neo4j で影響ノードを取得:

```cypher
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r]-(affected)
WHERE r.type IN ['applies-to', 'mandated-by', 'compliance-required', 'law_basis']
RETURN affected.nid AS node, r.type AS rel_type, r.weight AS weight
ORDER BY r.weight DESC
```

影響ノードを 3 種類に分類:

| 分類 | 意味 | アクション |
|---|---|---|
| 高インパクト (weight ≥ 0.8) | 重要な依存関係 | 個別レビュー必須 |
| 中インパクト (0.4-0.8) | 関連あるが調整可能 | 一括確認 |
| 低インパクト (< 0.4) | 参考程度 | サマリのみ |

### ステップ 5: relations 再評価

各影響ノードについて:

1. 現行 relations が新版でも有効か確認
2. 新版で追加された相関がないか確認
3. `weight` の調整案を生成
4. 提案形式:
   ```markdown
   ## relations 再評価提案
   
   ### [[10_People/P-0004]]
   - 維持: `applies-to [[障害者総合支援法]]` weight=1.0
   - 変更: `eligible-service [[66_Services/就労移行支援]]` weight=0.7 → 0.5
     （理由: 令和9年改正で就労系統合、対象要件が変わる可能性）
   - 新規提案: `considered [[66_Services/就労選択支援]]` weight=0.6
   ```

### ステップ 6: 承認とコミット

1. ユーザーに全提案を提示
2. 個別承認 / 一括承認 / 却下を受け付け
3. 承認分を実行:
   - frontmatter 更新
   - 本文更新
   - 関連ノートの relations 更新
4. commit メッセージテンプレート:
   ```
   feat(law): 障害者総合支援法を令和9年改正に更新
   
   - 旧版を archived/ に退避
   - 影響 12 ノートの relations を再評価
   - 新規サービス（就労選択支援）を追加
   
   一次ソース: {URL}
   施行日: 2027-04-01
   ```

## 例: 簡易実行コマンド

Claude Code 上で:

```
raw/laws/障害者総合支援法_令和9年改正.pdf で
60_Laws/障害者総合支援法.md を更新してください。
version: "令和9年改正", effective_date: 2027-04-01
```

## 出力フォーマット（最終報告）

```markdown
# 改正取込完了レポート

## 対象
- ノート: [[60_Laws/障害者総合支援法]]
- 版: 令和6年改正 → 令和9年改正
- 施行日: 2027-04-01

## 実施内容
- ✅ 旧版アーカイブ: archived/障害者総合支援法_R6.md 作成
- ✅ 新版反映: frontmatter + 本文更新
- ✅ amendment_history に新エントリ追加
- ✅ 波及分析: 12 ノートに影響
- ✅ relations 再評価: 8 件維持、3 件調整、1 件新規

## relations 変更内訳

### 維持（8件）
- ...

### 調整（3件）
- [[P-0004]] eligible-service [[就労移行支援]] weight 0.7 → 0.5

### 新規（1件）
- [[P-0004]] considered [[就労選択支援]] weight 0.6

## 次のアクション
- [ ] vault_health_check で整合性確認
- [ ] Neo4j 再同期
- [ ] 00_MOC/Home から改正告知バナーを除去
- [ ] 月次モニタリング時に利用者ごとの影響を確認
```

## 注意事項

### 必須遵守

- **一次情報のみを根拠に**: ブログ・SNS 情報は補助参考。改正は必ず官報・e-Gov・厚労省公式文書で確認
- **旧版を絶対に削除しない**: archived/ に保存し、`superseded_by` で新版とつなぐ
- **実名混入チェック**: 改正原文に含まれる委員名・参考人名は役割表現に置換
- **経過措置の明記**: 旧版と新版が併存する期間は `condition` フィールドで明確化
- **大規模改正時の段階取込**: 数百条の改正は数回に分けて、影響分析の質を保つ

### 差分が大きい場合の扱い

制度設計が根本的に変わる場合（例: 新法創設・抜本改正）:
- 既存ノートを更新せず、**新規ノートを作成**
- 旧ノートに `superseded_by` を付けて archived/ に退避
- `derived-from` relation で旧法との系譜を明示

### 報酬改定（3 年ごと）の一括処理

全 `66_Services/*.md` を対象にする場合:
1. 新報酬告示 PDF を `raw/services/` に配置
2. `/law-amendment-integrate` を対象一覧で一括実行
3. 各サービスノートの `version`, `fee_code`, `unit_price` 等を更新
4. 影響する利用者の `currently-using` relation をレビュー

## 関連

- [[amendment-watch]]: 改正検知
- [[raw-to-wiki]]: 原文 → wiki 化
- [[vault-health-check]]: 整合性確認
- [[90_Meta/amendment-tracking]]: 設計書
