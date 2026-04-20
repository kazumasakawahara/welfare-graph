---
name: vault-health-check
description: vault 全体の品質をチェックし、期限切れ・孤児ノート・壊れた wikilink・スキーマ違反・relations 整合性を検出してレポートを生成する。計画相談専門員が月次・四半期ごとに実行する想定。
---

<!-- allow-realname -->

# vault-health-check skill

## 用途

vault のメンテナンスに必要な診断を一括実行:

- **期限管理**: `review_due` 超過・近接の検出
- **スキーマ準拠**: 必須 frontmatter 欠損検出
- **リンク健全性**: 壊れ wikilink・孤児ノートの検出
- **relations 整合性**: 重み・型辞書違反・双方向性チェック
- **仮名化**: 実名混入の追加スキャン（`realname-check` の統合）
- **成長指標**: ページ数・relations 密度の時系列変化

月次 or 四半期で実行し、運用を健全に保つ。

## 入力

- 焦点（任意）: `laws` / `services` / `methods` / `all`（デフォルト `all`）
- 重大度閾値（任意）: `critical` / `warning` / `info`（デフォルト `warning` 以上を報告）
- 保存先（任意）: `90_Meta/health-reports/YYYY-MM-DD.md`（デフォルト）

## 出力フォーマット

```markdown
# vault health-check レポート

**実行日時**: {YYYY-MM-DD HH:MM}
**焦点**: {all / laws / ...}
**対象ファイル数**: {N}

---

## 🔴 CRITICAL（要即対応）

### 1. review_due 超過

- [[60_Laws/xxx]]: 2024-04-01（超過 N日）
- [[66_Services/yyy]]: ...

### 2. 必須フィールド欠損

- [[xxx]]: `source_url` が空 (law層は必須)

### 3. 実名混入の疑い

- [[xxx]]: パターン「〇〇 〇〇」検出

---

## 🟡 WARNING（要計画的対応）

### 4. review_due 近接（30日以内）

- [[xxx]]: 2026-05-15（残り25日）

### 5. 壊れた wikilink

- [[xxx]] から [[yyy]] への参照が未解決（yyy が存在しない）

### 6. 孤児ノート（relations も被参照もなし）

- [[30_Insights/xxx]]

### 7. relations の weight 範囲外

- [[xxx]] の relations[3]: weight = 1.2（範囲: 0.0-1.0）

---

## 🟢 INFO（参考情報）

### 8. 成長指標

| 層 | 前回 | 今回 | 増減 |
|---|---|---|---|
| 60_Laws | 6 | 9 | +3 |
| ... |

### 9. relations 密度

- 平均 relations/ノート: 3.2
- 最密ノート: [[P-0001]] (21 relations)
- 最疎ノート: [[xxx]] (0 relations)

### 10. 型辞書カバレッジ

- `relations.type` 使用実績:
  - applies-to: 45件
  - compliance-required: 23件
  - ...
- 辞書外使用: なし / ありの場合は警告

---

## 🎯 推奨アクション

### 最優先（今週中）
- [ ] CRITICAL #1, #2, #3 対応

### 計画的（今月中）
- [ ] WARNING #4 の review_due 更新
- [ ] WARNING #5 の wikilink 修正
- [ ] WARNING #6 の孤児ノート処理（統合 or 削除 or 参照追加）

### 継続観察
- [ ] INFO #8 の成長記録を次回比較
```

## 実行手順（Claude 向け）

### 1. 対象ファイル収集

- 全 `.md` ファイルを Glob で収集（90_Meta/ を除く）
- frontmatter を解析（YAML として）

### 2. CRITICAL チェック

#### 2.1 review_due 超過
- 全 `review_due` フィールドを取得
- **今日より過去** の日付のものをリスト
- 超過日数を計算

#### 2.2 必須フィールド欠損

層別の必須フィールド（`90_Meta/SCHEMA.md` 参照）:

```yaml
law:        [source_url, version, effective_date, review_due, issuer]
guideline:  [issuer, source_url, version, effective_date, review_due]
service:    [law_basis, target, version, review_due]
framework:  [origin, year, domain]
disorder:   [icd11_code OR dsm5_code]
method:     [evidence_level, target_disorder]
assessment: [administrator, time_required, purpose]
org:        [role, mandate]
person:     [id, status, diagnosis]
```

欠損を検出したらリストアップ。

#### 2.3 実名混入

- `realname-check` スキル相当のパターン検出
- `<!-- allow-realname -->` がある場合はスキップ
- 知識層・MOC では誤検出しやすい（空白区切り漢字）→ タグ・frontmatter内は除外

### 3. WARNING チェック

#### 3.1 review_due 近接
- 30日以内に期限を迎える `review_due`

#### 3.2 壊れ wikilink
- 本文・frontmatter の wikilink 抽出: `\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]`
- リンク先ファイルの存在確認
- 該当しないものをリスト

ただし `stub`（空ファイル）と `broken`（ファイルなし）は区別:
- stub: ファイルはあるが空 → WARNING（いずれ埋める前提）
- broken: ファイルが存在しない → CRITICAL or WARNING（タイポ or 未作成）

#### 3.3 孤児ノート
- `relations` が空 AND 他ノートから wikilink で参照されていない
- ただし以下は除外:
  - README.md（各層の目次）
  - MOC（意図的にルーター機能）
  - alias_map.md 等の Meta

#### 3.4 relations weight 範囲外
- `weight < 0.0` または `weight > 1.0` を検出

#### 3.5 relations type 辞書違反
- `90_Meta/SCHEMA.md` のリンク型辞書に記載の type 以外
- 辞書を拡張すべきか、typo か判断

### 4. INFO 集計

#### 4.1 層別ページ数
- `6[0-7]_*/*.md`, `[1-5][0-9]_*/*.md` をカウント

#### 4.2 relations 密度
- 全 person ノートの relations 件数の平均・最大・最小
- 全ノート全体の平均

#### 4.3 type 辞書の使用実績
- `relations.type` の集計
- 辞書の使用状況

### 5. 過去レポートとの比較

- `90_Meta/health-reports/` の最新2件を比較
- 前回から今回の変化を INFO に記載

### 6. レポート生成

- 形式: `90_Meta/health-reports/YYYY-MM-DD.md`
- frontmatter に実行日時・重大度サマリ

### 7. 推奨アクションの自動生成

検出された問題を優先度別に列挙:
- CRITICAL は「今週中」
- WARNING は「今月中」
- INFO は「継続観察」

## 実行時の工夫

### パフォーマンス

- 大規模 vault で遅い場合、層単位で分割実行
- Glob で層を絞り込み（例: `60_Laws/*.md`）

### 誤検出削減

- 実名検出は知識層で false-positive 多発 → `<!-- allow-realname -->` 前提
- 孤児ノート判定で README/MOC/Meta を除外

### Obsidian との併用

- Obsidian の **Graph View** で孤児ノートが視覚的に見える（グループ化で確認可）
- **Backlinks pane** で個別ノートの被参照確認
- 本スキルは一覧性・記録性でこれを補完

## 保存と履歴

- `90_Meta/health-reports/YYYY-MM-DD.md` に定期保存
- frontmatter に `type: meta, tags: [health-report]`
- 過去レポートとの比較で成長・改善トレンド把握

## 関連スキル

- `realname-check`: 実名混入の専用スキャン（本スキルと統合運用）
- `visit-prep`: 訪問前の個別準備（本スキルとは独立）
- `support-hypothesis`: 支援仮説生成（本スキルで健全性保証）

## 禁忌・注意事項

- 実名を誤検出した場合も、レポート出力には具体文字列を書かず「疑い箇所」とだけ記載
- `90_Meta/alias_map.md` は **読まない** （Meld Encrypt で暗号化）
- レポート自体を git コミット対象にする場合、誤検出由来の実名混入に注意

## 将来拡張

- 自動修復（review_due を定期更新期限まで自動延長、ただし法令は手動）
- Graph 中心性の計算（どのノートが支援に重要か）
- 層間のリンク密度バランス分析
