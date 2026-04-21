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
