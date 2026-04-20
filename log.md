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
