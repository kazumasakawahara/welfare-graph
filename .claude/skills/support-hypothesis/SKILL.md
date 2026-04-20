---
name: support-hypothesis
description: 対象当事者（P-XXXX）の frontmatter relations を重みと意味付けに沿って辿り、知識層（60_Laws / 61_Guidelines / 63_Disorders / 64_Methods / 66_Services / 67_Orgs）を横断して「根拠付き支援仮説」を生成する。4レンズ（法令適合 / サービス適格 / 支援技法マッチング / 類似事例）で分析し、すべての主張に wikilink 出典を付す。計画相談専門員が支援計画作成・見直し時に使う想定。
---

<!-- allow-realname -->

# support-hypothesis skill

## 用途

P-XXXX の `relations` を根拠に、以下の支援仮説を自動生成する:

- 現在の支援計画で **法令・ガイドライン適合** は十分か（コンプライアンスチェック）
- 本人に **他に適格なサービス** がないか（サービス適格診断）
- 障害特性×状況に **最適な技法** が当てられているか（技法マッチング）
- 類似ケースで **効果があった／なかった支援** は何か（類似事例抽出）

仮説はあくまで候補。最終判断は担当相談員と関係機関の合意形成で決めるべきという前提を必ず明示する。

## 入力

- 当事者ID（必須）: 例 `P-0001`
- 焦点テーマ（任意）: `sexuality` / `employment` / `housing` / `medical` / `crisis` 等
  - 指定時は該当論点に特化した仮説を生成
- 上位N件制限（任意・デフォルト5）: 各レンズで提示する仮説数の上限

## 出力フォーマット

```markdown
# 支援仮説: {P-XXXX}

**生成日時**: {YYYY-MM-DD HH:MM}
**焦点テーマ**: {指定あれば / なければ「総合」}
**対象 relations 件数**: {件数}

> ⚠️ **免責**: 本出力は LLM による relations トラバースに基づく支援仮説候補。最終判断は [[計画相談支援]] の担当者・行政・主治医・弁護士等の合議で行うこと。法的助言ではない。

---

## 🔒 レンズ①: 法令適合・コンプライアンス

本人に適用される法令・ガイドラインのうち、**compliance-required / mandatory-report-trigger** で weight ≥ 0.8 のもの:

### 義務的対応

- **[[60_Laws/xxx]]**（weight: 1.0, evidence: "..."）
  - 想定される現場実装: ...
  - 確認方法: ...
  - 記録要件: ...

### 推奨的対応

- ...

### 📌 直ちに確認すべきチェック項目

- [ ] 項目1（根拠: [[61_Guidelines/xxx]]）
- [ ] 項目2

---

## 🎯 レンズ②: サービス適格診断

本人に適用しうるサービスを `applies-to` / `eligible-service` / `considered` から抽出:

### 現在利用中

| サービス | 事業所 | 適格根拠 | 評価 |
|---|---|---|---|
| [[66_Services/xxx]] | [[O-XXXX]] | ... | ... |

### 適格あり・未利用（検討候補）

| サービス | 適格根拠 | 推奨度 | 導入時の留意 |
|---|---|---|---|
| [[66_Services/xxx]] | weight: 0.85, "..." | ★★★ | ... |

### 状況次第

| サービス | 適格条件 | 確認事項 |
|---|---|---|
| [[66_Services/xxx]] | weight: 0.3, "..." | 再アセスメント |

### ⚠️ 65歳問題・制度移行の要注意

- 該当あり/なし
- 内容: ...

---

## 🧩 レンズ③: 支援技法マッチング

障害特性 × 推奨技法 × 禁忌技法 の整合チェック:

### 推奨される技法（evidence-based / recommended）

1. **[[64_Methods/xxx]]**
   - 根拠: [[63_Disorders/xxx]] への responds-to（weight: 0.9）
   - 背景理論: [[62_Frameworks/xxx]]
   - 現場適用Tips: ...
   - 実施の要件: 研修修了・対応可能事業所 等

### 禁忌・注意が必要な技法（contraindicated）

- **技法Y**: [[63_Disorders/xxx]] では contraindicated
  - 理由: ...
  - 観察ポイント: 事業所で実施されていないか

### 既存計画との Gap 分析

- 現計画で採用されている技法: ...
- 採用されていないが有効と思われる技法: ...
- Gap の根拠: ...

---

## 📚 レンズ④: 類似事例からの学び

`30_Insights/` から、同じ障害特性・同じ課題テーマを扱った知見を抽出:

### 成功パターン

- **[[30_Insights/xxx]]**: 概要 / 適用条件 / 効果の出方

### 失敗・再検討パターン

- **[[30_Insights/xxx]]**: 何が機能しなかったか

### 本ケースへの転用可能性

- 転用可: ...
- 転用時の調整: ...

---

## 🧭 統合的な支援仮説（3-5 個）

レンズを横断した具体的な支援仮説:

### 仮説A: {短い名前}

- **WHY（根拠）**: [[xxx]] × [[yyy]] の交差
- **WHAT（内容）**: 何を変える / 追加する
- **HOW（手順）**: 段階的な導入ステップ
- **WHO（責任）**: C-XXXX / O-XXXX / F-XXXX の役割
- **WHEN（時期）**: 次回モニタリング / 3か月後 / 等
- **RISK（留意）**: 想定される副作用・失敗シナリオ
- **EVIDENCE（信頼度）**: 高 / 中 / 低 + 理由

### 仮説B-E: 同様の構造

---

## ❓ 追加確認が必要な情報

relations が不足していて仮説生成に不確実性が残る項目:

- [ ] 本人の xxx への意思（[[61_Guidelines/意思決定支援ガイドライン]]）
- [ ] 家族の xxx への受容度
- [ ] 事業所の xxx 対応可否
- [ ] 最新の yyy アセスメント

---

## 📎 参照 relations（全件リスト）

frontmatter から抽出した relations を weight 降順で:

| to | type | weight | evidence |
|---|---|---|---|
| [[xxx]] | applies-to | 1.0 | ... |
| ...

---

**次回モニタリングまでに**: 仮説 A〜E のうち着手候補を担当者会議で選定
```

## 実行手順（Claude 向け）

### 1. 対象ノートを読む

- `10_People/{id}.md` を Read
- frontmatter から `relations` 配列全体を取得
- `diagnosis` / `disability_cert` / `primary_supporter` / `service_plan_id` も取得

### 2. relations をレンズ別に分類

`type` フィールドでバケット分け:

**レンズ①（法令・コンプラ）**:
- `compliance-required`, `mandatory-report-trigger`, `applies-to`（法令側）

**レンズ②（サービス適格）**:
- `eligible-service`, `currently-using`, `considered`, `discontinued`, `supersedes-at`

**レンズ③（技法マッチング）**:
- `recommended`, `evidence-based`, `responds-to`（技法側）, `contraindicated`

**レンズ④（類似事例）**:
- `relations` だけでなく、`30_Insights/` を Grep 検索
  - `has-characteristic` の障害特性ページを経由し、同じ障害特性に言及する Insight を横展開

### 3. 関連知識層ページを Read

`relations[*].to` の wikilink 先をすべて Read し、以下を抽出:

- **法令ページ**: 義務条項・通報義務・三要件 等
- **ガイドラインページ**: チェックリスト・記録要件
- **サービスページ**: target（支給決定基準）・65歳問題
- **障害特性ページ**: responds-to / contraindicated の技法リスト
- **技法ページ**: evidence_level / training_required
- **関係機関ページ**: referral_routes / escalate 条件

重要: 本人 diagnosis（例: 知的障害・自閉スペクトラム症）から、`63_Disorders/` の該当ページも自動で辿る（relations に明記されていなくても）。

### 4. Gap 分析

- 現計画（frontmatter の `currently-using`）と推奨（`recommended` / `evidence-based`）の差
- 法令適合で未実施項目
- 65歳問題等の制度変更予兆

### 5. 類似事例抽出

- `30_Insights/` を Grep で主要タグ（障害特性・支援技法）で検索
- `20_Episodes/` で同じ障害特性の他 P-XXXX の事例を Grep（任意、パフォーマンスに応じ）

### 6. 焦点テーマ（引数あり時）

- `sexuality` → [[00_MOC/Sexuality]] を Read し、該当関連層のページに絞り込み
- `employment` → 66_Services/就労系 + 67_Orgs/就ポツ等に絞り込み
- `housing` → 66_Services/共同生活援助・施設入所 + 50_Resilience/ に絞り込み
- `medical` → 66_Services/精神通院医療 + 63_Disorders/ 医療関連
- `crisis` → 61_Guidelines/虐待防止・身体拘束 + 67_Orgs/基幹相談・ワンストップ

### 7. 統合仮説の生成

- 3〜5個の仮説を、レンズ横断で作る
- 各仮説に **WHY / WHAT / HOW / WHO / WHEN / RISK / EVIDENCE** を記述
- 信頼度は、根拠 relations の weight と出典数から自動評価:
  - 高: weight ≥ 0.85 の根拠が複数
  - 中: weight ≥ 0.7 の根拠あり
  - 低: weight < 0.7 または根拠 relations が単発

### 8. 免責・注意の固定文言を必ず挿入

冒頭の「⚠️ 免責」ブロックを省略しない。

### 9. 保存場所（任意）

- 保存希望時: `30_Insights/hypotheses/{YYYY-MM-DD}_{id}_support-hypothesis.md`
- デフォルトは標準出力のみ

## 禁忌・注意事項

### 絶対に守る

- **実名を一切出力しない**（alias_map を参照しない）
- **法的助言と誤認させる表現を避ける**（「〜すべき」→「〜を検討」に）
- **本人意思を飛び越えた提案をしない**: 意思決定支援の文脈で「本人との対話」を前提に
- **断定を避ける**: 「適格の可能性が高い」「要再アセスメント」等の確率的表現

### relations に頼りすぎない

- relations に記載がない = 存在しないではない
- 「追加確認が必要な情報」セクションで不足を明示
- 特に本人の意思・家族の受容度・事業所の対応可否は relations に書きづらい → 必ず確認項目に挙げる

### 焦点テーマ sexuality の取扱い

- [[00_MOC/Sexuality]] の4柱（権利・教育・予防・対応）で整理
- 被害の疑いがある場合は **[[61_Guidelines/障害者虐待防止マニュアル]]** の通報フローを優先表示
- 「予防」より「権利」を前置き（過保護の警戒）

### 重みの解釈

- weight ≥ 0.95: 義務（法令・絶対的禁忌）
- weight 0.80-0.94: 強い推奨
- weight 0.60-0.79: 検討に値する
- weight 0.40-0.59: 弱い示唆
- weight < 0.40: 記録のみ、仮説生成には使わない

## 出力品質のセルフチェック

出力前に以下を自問:

- [ ] すべての主張に wikilink 出典があるか
- [ ] 免責文言が冒頭にあるか
- [ ] 仮説は3〜5個に収まっているか（多すぎ注意）
- [ ] 本人の意思確認プロセスが組み込まれているか
- [ ] 65歳問題・制度移行の論点を見落としていないか
- [ ] 類似事例が見つからなかった場合「なし」と明示しているか
- [ ] 禁忌技法（contraindicated）が現計画で採用されていないか確認しているか
- [ ] 実名・個人情報が混入していないか

## 将来拡張（未実装）

- Neo4j 連携でグラフ走査を機械化
- Dataview クエリの自動生成
- モニタリング時の差分比較（前回仮説との対比）
- 事業所選定への具体的提案（40_Stakeholders/ 横断）
