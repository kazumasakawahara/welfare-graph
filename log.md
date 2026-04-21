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
