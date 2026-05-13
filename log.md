<!-- allow-realname -->
# welfare-graph 操作ログ

append-only な運用ログ。**削除・編集禁止**。新規エントリは末尾に追加。

## 書式

```
### YYYY-MM-DD HH:MM [mode] 一行サマリ

- 詳細
- 詳細
```

### mode（[[CLAUDE#§3 動作モード（5 + 2）]] 参照）

- `[ingest]` raw → wiki 取り込み
- `[query]` 照会・回答生成
- `[lint]` 健全性チェック
- `[overview]` overview.md 再生成
- `[save]` 会話保存
- `[amendment-watch]` 改正監視
- `[law-amendment-integrate]` 改正取込
- `[manual]` 手作業の編集（スキル経由でない変更）
- `[schema]` スキーマ変更
- `[script]` スクリプト追加・改修

---

## ログ本体

### 2026-04-20 [manual] welfare-graph vault 初期化

- 9 層アーキテクチャ（00_MOC / 10_People / 20_Episodes / 30_Insights / 40_Stakeholders / 50_Resilience / 60_Laws / 61_Guidelines / 62_Frameworks / 63_Disorders / 64_Methods / 65_Assessments / 66_Services / 67_Orgs / 90_Meta）を確立
- SCHEMA.md §1-§6 を作成
- 架空利用者 P-0001 / P-0002 / P-0003 を作成
- CSS snippet (layer-colors) を導入
- Obsidian Meld Encrypt プラグインで alias_map.md を暗号化
- Neo4j 連携（sync_to_neo4j.py + neo4j-integration-design.md）
- .claude/skills/ に 7 スキル配置（support-hypothesis, vault-health-check, ecomap-from-relations, visit-prep, monthly-summary, realname-check）

### 2026-04-20 [schema] 改正追随機構の導入（進化する知識グラフ）

- SCHEMA.md §7 に改正追随フィールドを追加（version_hash, amendment_history, supersedes, superseded_by, status）
- 90_Meta/amendment-tracking.md を作成（4 層アーキテクチャ: 検知/差分/統合/通知）
- 90_Meta/scripts/amendment_check.py を新規実装
- .claude/skills/amendment-watch / law-amendment-integrate を追加
- 60_Laws/archived/ フォルダ運用を確立
- 障害者総合支援法 H30 版を archived に退避（実例）
- CONTRIBUTING.md + .github/ISSUE_TEMPLATE + PR_TEMPLATE + monthly-health-check.yml 追加

### 2026-04-20 [ingest] 就労選択支援関連ページの新設

- raw/guidelines/2024_就労選択支援_運営ガイドライン_素案メモ.md を入力資料として配置
- 61_Guidelines/就労選択支援_運営要綱.md に変換（改正追随フィールド完備）
- 66_Services/就労選択支援.md を新規作成（令和6年改正で新設サービス）
- 改正追随運用の実例として機能

### 2026-04-20 [script] welfare-graph MCP サーバーの実装

- mcp_server/ ディレクトリに Python パッケージを構築（Python 3.10+, mcp SDK 依存）
- 10 tools（search_vault / support_hypothesis / find_applicable_laws 等）
- 11 resources（MOC + 運用設計書）
- 3 prompts（consult_for_person / check_legal_compliance / find_local_services）
- プライバシー設計: プライベート層（10_People/ 20_Episodes/ 等）は MCP 経由で公開しない
- docs/MCP_SETUP.md（Claude Desktop/Code/Cursor 設定ガイド）
- skill_templates/welfare-graph-consult/SKILL.md（グローバル Skill テンプレ）

### 2026-04-20 [manual] data-wiki/CLAUDE.md 準拠性監査および CLAUDE.md 策定

- data-wiki/CLAUDE.md との差分分析を実施
- welfare-graph 独自 CLAUDE.md を vault ルートに策定（LLM Wiki パターン + 9 層アーキテクチャ + 改正追随機構を統合）
- log.md（本ファイル）を新設（append-only 操作ログ）
- 90_Meta/taxonomy.md（ドメインタグ体系）を新設
- SCHEMA.md にコールアウト規約（§8）を追記
- .claude/skills/conversation-save/ を追加（save モード実装）
- 90_Meta/scripts/generate_overview.py + overview.md を追加
- raw/notes/ サブフォルダを新設

### 2026-04-21 [ingest] 合理的配慮関連判例 2 件の取り込み

- raw/jskr_01_08.pdf → `raw/insights/2020_川崎就学訴訟_今川論文.pdf` にリネーム保管
- `30_Insights/川崎就学訴訟_インクルーシブ教育と合理的配慮.md` を新規作成
  - 出典: 今川奈緒『人文社会科学論集』1, pp.93-104（茨城大学, 2022）
  - 対象判決: 横浜地判令和2年3月18日（人工呼吸器児の認定特別支援学校就学者指定の違法性）
  - 論点: インクルーシブ教育を受ける利益／適正手続（憲法13条・31条、米国IDEA参照）／裁量審査密度
  - relations: 障害者差別解消法 / ICF / 00_MOC/Knowledge
- raw/障害者に求められる合理的配慮義務...md → `raw/insights/2022_Man_to_Man_Animo事件_ASK川崎解説.md` にリネーム保管
- `30_Insights/Man_to_Man_Animo事件_雇用における合理的配慮義務.md` を新規作成
  - 出典: 弁護士法人ASK川崎 コラム（2024-04-02更新）
  - 対象判決: Man to Man Animo 事件・岐阜地判令和4年8月30日
  - 論点: 合理的配慮に準ずる義務／支援・指導と配慮要望の衝突の判断枠組み
  - relations: 障害者差別解消法 / 就労移行支援 / 就労定着支援 / 就労継続支援A型 / 障害者就業・生活支援センター / ハローワーク
- 実名の扱い: 学術論文著者（今川奈緒）は公人情報として維持、訴訟当事者は役割表現（原告児童・保護者・原告労働者A・被告事業者B社）

### 2026-04-21 [ingest] 合理的配慮ハブページの新設

- `62_Frameworks/合理的配慮.md` を新規作成
  - 根拠: 障害者権利条約 2 条、障害者差別解消法 7/8 条、障害者雇用促進法 36 条の 2/3
  - 構成要素: 意思表明／過重な負担／建設的対話／合意形成
  - 領域別ガイド: 教育・雇用・福祉サービス・行政・商業
  - 判例との接続: 川崎就学訴訟・Man to Man Animo 事件
  - relations: 11 本（mandated-by: 差別解消法、complements: ICF/PCP/意思決定支援GL/両判例、applies-to: 就労系サービス・センター）
- 既存ページへの逆参照追加
  - `30_Insights/川崎就学訴訟_インクルーシブ教育と合理的配慮.md` → `[[62_Frameworks/合理的配慮]]` (complements, 0.95)
  - `30_Insights/Man_to_Man_Animo事件_雇用における合理的配慮義務.md` → `[[62_Frameworks/合理的配慮]]` (complements, 0.95)
  - `60_Laws/障害者差別解消法.md` → `[[62_Frameworks/合理的配慮]]` (applies-to, 0.95)
- 品質: CRITICAL 0 / WARNING 0、124 ノート / 377 relations

### 2026-04-21 [ingest] 合理的配慮グラフの周辺補完（6ページ新設）

**背景**: 新規 2 判例と合理的配慮 FW が参照する法令・障害特性が欠落しており、グラフ上で関係が断線していた。

**新規作成（6ページ）**:

- `60_Laws/障害者権利条約.md` — 2006 国連採択/2014 日本批准。2条（合理的配慮の国際定義）・5条・9条・12条・19条・24条・27条・33条。2022 総括所見（強制入院・分離教育・代行決定への懸念）
- `60_Laws/障害者雇用促進法.md` — 昭和35制定/平成25・令和4改正。36条の2・3・4（合理的配慮・過重負担・意向確認）。2024改正法定雇用率引上げ（2.5%→2.7%）
- `60_Laws/障害者基本法.md` — 昭和45制定/平成23大幅改正。社会モデル導入、4条（差別禁止）・16条（教育）・29条（司法手続）。上位基本法として機能
- `60_Laws/医療的ケア児支援法.md` — 令和3年制定・施行。医療的ケア児支援センターの法的根拠。川崎就学訴訟以後の就学判断枠組みの質的変化
- `63_Disorders/高次脳機能障害.md` — 厚労省診断基準2008。注意・記憶・遂行機能・社会的行動障害。代償手段・認知リハ・精神手帳
- `63_Disorders/強迫性障害.md` — DSM-5-TR/ICD-11 (6B20)。強迫観念・強迫行為。ERP（曝露反応妨害法）が第一選択、家族巻き込み解消

**既存ページ更新（cross-link）**:

- 川崎就学訴訟: `applies_to_disorders` に重症心身障害、relations に権利条約・基本法・医療的ケア児支援法を追加
- Man to Man Animo 事件: `applies_to_disorders` に高次脳機能障害・強迫性障害、relations に雇用促進法・2 障害を追加
- 合理的配慮 FW: relations に権利条約（mandated-by, 1.0）・基本法（mandated-by, 0.9）・雇用促進法（mandated-by, 0.95）を追加
- `00_MOC/Knowledge.md`: 「権利擁護・合理的配慮」セクション新設、法令階層＋判例ノード＋障害特性を明示
- `00_MOC/Timeline.md`: 2006〜2026 の権利擁護関連制度・判例タイムライン（14 項目）を追加

**品質**: CRITICAL 0 / WARNING 0、130 ノート / 431 relations、Neo4j 同期済

### 2026-04-21 [manual] ページ作成原則の策定（mantra 化）

**背景**: 同日の合理的配慮 FW + 周辺 6 ページの作成を振り返り、河原より「投機的作成は LLM Wiki パターンに反するのでは」との指摘。対話を経て「いつか必要」は「今は不要」と同義という mantra を合言葉として運用文書に焼き付けることを決定。

**新規作成**:

- `90_Meta/page-creation-principles.md` — 9 章構成の運用原則
  - §1 投機的作成を禁じる理由（LLM Wiki パターンの核心 / 投機的作成の 5 つの害 / 壊れリンクの設計上の役割）
  - §2 3 つの関門（Q1 今日の実務で助かったか / Q2 raw に原典あるか / Q3 次に誰がいつ困るか）
  - §3 作成時の必須手続き（frontmatter `triggered_by` / 本文冒頭の作成コンテキスト / 粒度節度 100-150 行）
  - §4 昇格プロセス（Day 0 壊れリンク → Day N raw 整備 → ingest）
  - §5 間引き・降格（active → provisional → archived）
  - §6 例外（MOC・90_Meta・README・templates）
  - §7 セルフチェックリスト 7 項目
  - §8-9 改訂履歴・関連

**既存更新**:

- `CLAUDE.md` §2 に #11 として mantra + 必要十分条件 2 点 (raw/ 原典・実務エピソード要請) を追記
- `.claude/skills/raw-to-wiki/SKILL.md` 冒頭に mantra と 3 関門への参照を追加

**影響**: 今後の ingest 指示は本原則に従い、投機的作成は壊れリンク維持へと方針転換。次回以降の判断基準として 7 項目セルフチェック（6 つ以上 Yes で作成可）を適用。

### 2026-05-11 [meta] PR #1 レビュー対応 — page-creation-principles 導入と本 PR 補完作業の関係を明示

**背景**: PR #1（合理的配慮グラフ新設）のレビューにおいて、同 PR が同時導入する `page-creation-principles.md` §2 Q1 (今日の実務で助かったか) と §1.3 (壊れリンクは設計されたバッファ) と、判例 2 件のために 法令 4 + 障害特性 2 を **先回り作成** している作業実態が緊張関係にあるとの指摘を受けた。

**解釈の確定**:

本 PR の補完作業（法令 4・障害特性 2 の新設）は、**page-creation-principles の運用開始前** に判例 ingest を完成させるための「過渡期作業」として実施。具体的には:

- 判例ノート（川崎就学訴訟・Man to Man Animo 事件）に必要な wikilink 解決を、**当時の運用**（リンク先がなければハブを補完する）で先に進めた
- その作業を振り返って原則を成文化したのが page-creation-principles.md
- したがって本 PR の補完は原則に **準拠していない** が、**原則導入のトリガーとなった事例**である

**本 PR 以降の運用**:

- 新規ページ作成は §2 の 3 関門 (Q1 実務 / Q2 raw 原典 / Q3 次に誰が困るか) を厳格適用
- 既存ページに wikilink を追加する際、参照先がなければ **壊れリンクのまま残す** ことを既定動作とする
- 壊れリンク先のページを作るのは、§2 を満たす実務エピソードが新たに発生した時のみ

**追加レビュー対応**（本コミット群で実施）:

- PR #1 レビューで指摘された 5 項目に対応:
  1. `62_Frameworks/合理的配慮.md` のフォルダ末尾形 wikilink 2 件を具体ページ列挙に修正
  2. `vault_health_check.py` にフォルダ末尾形 wikilink 検出を追加（再発防止、独立カテゴリで 18 件可視化）
  3. `63_Disorders/高次脳機能障害.md` / `強迫性障害.md` に `source_url` + `source_citation` + `secondary_sources` を追加
  4. `CLAUDE.md` §2 ガードレール 1 の文言を新規追加可否について明確化（既存 READ-ONLY / 新規承認制）
  5. 本エントリの追記（page-creation-principles と本 PR 補完作業の関係を明示）

### 2026-05-13 [lint] PR #1 マージ + フォローアップ PR #2 起票

**PR #1 マージ**: `3949b77` として main にマージ済。9 コミット・19 ファイル・+2,557/-48 行が確定。

**PR #2 フォローアップ（軽量補正）**:

mantra「いつか必要は今は不要と同義」を実地適用した最小限の修正:

1. **H1（H1 雇用率テーブル）の安全策**: `60_Laws/障害者雇用促進法.md` 43条以下のテーブルに `> [!warning] 数値は要原典確認` を挿入。記憶ベースの数値が運用判断に直接使われるリスクを警告。
2. **H3（権利委員会日付）**: `60_Laws/障害者権利条約.md` 「2022年9月」→「2022年10月」に修正、CRPD/C/JPN/CO/1 採択日（10月7日）と審査日（8月22-23日）を分離明記。
3. **L1（条約発効日）**: `00_MOC/Timeline.md` 「批准1/20（2014年1月）」と「効力発生2/19（2014年2月）」を 2 行に分離。
4. **6 派生ページに provisional 化**: `60_Laws/障害者権利条約` / `障害者雇用促進法` / `障害者基本法` / `医療的ケア児支援法` / `63_Disorders/高次脳機能障害` / `強迫性障害` の frontmatter に `status: provisional` と `triggered_by: "PR #1 — 原則策定前の補完作成（過渡期）"` を追加。
5. **`vault_health_check.py` 拡張**: WARNING カテゴリ「9b. 投機的作成疑い」を新設。`status: active` かつ `triggered_by` 未記入のページを検出（MOC / meta / person / episode 除外）。

**今回の検査結果**:
- CRITICAL 0 / WARNING 115（前回 18）
- 増加分 97 件は新指標「投機的作成疑い」の baseline 検出。既存層ノートが新原則に未整合であることの可視化。
- 6 派生ページは `status: provisional` のため検出から除外される（意図通り）。

**方針**: この PR #2 で「短期 health 安全策」と「長期 lint インフラ」を提供。以後の補正は **実需要発生時** に raw/ → ingest サイクルで実施。M2-M5 の指摘事項は意図的に未修正のまま残す。

### 2026-05-13 [lint] PR #2 レビュー対応: 9b カットオフ適用 + needs-driven 3 ページに triggered_by 補完

レビューで「9b の 97 件は原則の遡及適用で、mantra の趣旨と逆」との指摘を受け以下を実施:

1. **`vault_health_check.py` に `PRINCIPLES_EFFECTIVE_DATE = 2026-04-21` を導入**: 9b 検知を策定日以降に created されたページに限定。過去ノートは「原則施行前」として尊重し遡及しない。
2. **needs-driven 3 ページに `triggered_by` を補完**:
   - `30_Insights/川崎就学訴訟_インクルーシブ教育と合理的配慮.md`: raw/insights/2020_川崎就学訴訟_今川論文.pdf の ingest 指示
   - `30_Insights/Man_to_Man_Animo事件_雇用における合理的配慮義務.md`: raw/insights/2022_Man_to_Man_Animo事件_ASK川崎解説.md の ingest 指示
   - `62_Frameworks/合理的配慮.md`: 2 判例 + 差別解消法から参照される概念ハブ欠落の user 指摘

結果: WARNING 115 → 18 件（既存のフォルダ末尾形のみ）。9b は 0 件で原則の意図と完全一致。
