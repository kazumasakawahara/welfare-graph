<!-- allow-realname -->
# welfare-graph Vault 運用マニュアル

このファイルは `welfare-graph` Vault で作業するエージェント（Claude Code / Claude Desktop / Cursor 等）への操作指示書です。

設計思想は Karpathy「LLM Wiki」パターン + [`~/Obsidian/data-wiki/CLAUDE.md`](~/Obsidian/data-wiki/CLAUDE.md) の運用規約を、**障害福祉領域に特化した 9 層アーキテクチャ** に適用したものです。

---

## §1 Vault 構造

```
welfare-graph/
├── CLAUDE.md               # 本ファイル（運用マニュアル）
├── README.md               # プロジェクト概要
├── CONTRIBUTING.md         # コミュニティ協働ガイド
├── log.md                  # 操作ログ（append-only）
├── overview.md             # 俯瞰ダッシュボード（自動生成）
├── raw/                    # 生ソース（READ-ONLY — 絶対に書き換えない）
│   ├── laws/               # 法令原文
│   ├── guidelines/         # 厚労省ガイドライン
│   ├── services/           # サービス報酬告示
│   ├── insights/           # 判例・事例・Wikipedia 記事
│   ├── reports/            # 学会報告書
│   └── notes/              # 会話保存モード（§9 save）の保存先
├── 00_MOC/                 # Map of Content（ナビゲーション）
├── 10_People/              # 利用者ノート（P-XXXX・全て架空）【プライベート層】
├── 20_Episodes/            # エピソード記録【プライベート層】
├── 30_Insights/            # 抽象化された知見
│   └── hypotheses/         # 個別仮説【プライベート層】
├── 40_Stakeholders/        # 具体関係者【プライベート層】
├── 50_Resilience/          # 親亡き後設計【プライベート層】
├── 60_Laws/                # 法令【公開知識層】
│   └── archived/           # 改正前の旧版
├── 61_Guidelines/          # 厚労省ガイドライン【公開知識層】
├── 62_Frameworks/          # 理論フレームワーク【公開知識層】
├── 63_Disorders/           # 障害特性【公開知識層】
├── 64_Methods/             # 支援技法【公開知識層】
├── 65_Assessments/         # アセスメント【公開知識層】
├── 66_Services/            # 障害福祉サービス【公開知識層】
├── 67_Orgs/                # 関係機関【公開知識層】
├── 90_Meta/
│   ├── SCHEMA.md           # frontmatter 仕様 + リンク型辞書
│   ├── amendment-tracking.md   # 改正追随運用設計
│   ├── neo4j-integration-design.md
│   ├── neo4j-queries.md
│   ├── taxonomy.md         # ドメインタグ体系
│   ├── SETUP_COLORS.md
│   ├── alias_map.md        # 仮名↔実名（Meld Encrypt 暗号化）
│   ├── templates/          # ノート雛形
│   ├── scripts/            # Python ツール類
│   ├── health-reports/     # vault_health_check 出力
│   └── amendment-reports/  # amendment_check 出力
├── docs/                   # 利用者向けドキュメント
│   ├── USER_GUIDE.md
│   ├── MCP_SETUP.md
│   └── ANNOUNCEMENT_TEMPLATE.md
├── mcp_server/             # Claude Desktop/Code 向け MCP サーバー
├── .claude/
│   ├── skills/             # Claude Code スキル定義（9 種）
│   └── hooks/              # realname_detect 他
├── .obsidian/              # Obsidian 設定
└── .github/                # Issue/PR テンプレ + Actions
```

### プライベート層 / 公開知識層

| 分類 | 対象 | MCP 経由公開 | git コミット |
|---|---|---|---|
| **公開知識層** | 00_MOC, 30_Insights（汎用）, 60-67, 90_Meta 設計書 | ✅ | ✅ |
| **プライベート層** | 10_People, 20_Episodes, 30_Insights/hypotheses, 40_Stakeholders, 50_Resilience | ❌ | ✅（仮名 ID のみ） |
| **機密層** | 90_Meta/alias_map.md | ❌ | 暗号化版のみ |
| **原本** | raw/ | ❌ | .gitignore で PDF 除外 |

---

## §2 絶対遵守のガードレール

1. **`raw/` は READ-ONLY。** いかなる場合も書き換え・削除・移動しない
2. **wiki 側への書き込み前に必ず河原の承認を得る。** 承認なしの wiki 書き込みは禁止（例外: `raw-to-wiki` スキル内の明示承認プロセス）
3. **実名を wiki 本文に記載しない。** 仮名 ID（P-XXXX 等）のみ使用、実名は `90_Meta/alias_map.md`（Meld Encrypt 暗号化）のみ
4. **5 ファイル以上の同時変更は事前に一覧提示。** 影響範囲を列挙してから着手
5. **矛盾ソースは両論併記 + `> [!warning]` コールアウト。** 勝手に正誤判断しない
6. **大量更新時はバックアップ。** 20 ファイル以上の一括変更は事前に git commit + `archived/` または tag 退避
7. **削除は禁止。** 不要ページは `status: archived` に変更し `archived/` に退避
8. **改正は旧版を archived に退避してから行う。** 現行版を直接書き換えない（[[90_Meta/amendment-tracking]] §2 参照）
9. **法的助言・医学的助言に誤認される断定表現を避ける。** 「要検討」「担当相談員と協議」等を使用
10. **一次ソース URL を必ず frontmatter に記載。** `source_url` / `source` フィールド

---

## §3 動作モード（5 + 2）

### 基本 5 モード

#### 3.1 ingest（取り込み）

`raw/` に配置された一次資料を knowledge 層（60-67・30_Insights 等）に取り込む。

- 起動: `raw-to-wiki` スキル経由、または「raw/X.pdf を取り込んで」
- 詳細: [`.claude/skills/raw-to-wiki/SKILL.md`](.claude/skills/raw-to-wiki/SKILL.md)
- 必須: 承認ステップ（「取り込んでよいですか？」） / `log.md` への記録

#### 3.2 query（照会）

Vault 内から質問に回答を合成。

- Claude Desktop/Code から: welfare-graph MCP サーバー（`search_vault`, `support_hypothesis` 等）
- Obsidian 内から: 全文検索 `Cmd+Shift+F` + wikilink 辿り
- 詳細: [`docs/MCP_SETUP.md`](docs/MCP_SETUP.md) / [`mcp_server/README.md`](mcp_server/README.md)
- query 結果を残す場合: `30_Insights/hypotheses/YYYY-MM-DD_topic.md` に保存（プライベート層）

#### 3.3 lint（健全性チェック）

vault 全体の品質診断。

- 起動: `python3 90_Meta/scripts/vault_health_check.py` + `amendment_check.py`
- Claude 経由: `vault-health-check` スキル / `amendment-watch` スキル
- 自動実行: GitHub Actions 月次（`.github/workflows/monthly-health-check.yml`）
- 出力: `90_Meta/health-reports/YYYY-MM-DD.md` / `90_Meta/amendment-reports/YYYY-MM-DD.md`

#### 3.4 overview（概要再生成）

俯瞰ダッシュボードを更新。

- 起動: `python3 90_Meta/scripts/generate_overview.py`
- 出力: `overview.md`（層別件数・最近の取り込み・改正予告一覧・Mermaid グラフ）

#### 3.5 save（会話保存）

Claude との会話を `raw/notes/` に保存。

- トリガー: 「この会話を wiki に保存して」「このチャットを保存」等
- 保存先: `raw/notes/YYYY-MM-DD_トピック名.md`
- 詳細: [`.claude/skills/conversation-save/SKILL.md`](.claude/skills/conversation-save/SKILL.md) / 本マニュアル §9

### 拡張 2 モード（welfare-graph 固有）

#### 3.6 amendment-watch（改正監視）

- 起動: `amendment-watch` スキル / `amendment_check.py`
- 改正告知を検知して `status: pending-amendment` に更新

#### 3.7 law-amendment-integrate（改正取込）

- 起動: `law-amendment-integrate` スキル
- 旧版を `archived/` に退避 + 新版反映 + relations 再評価

---

## §4 ページフォーマット

### 全ページ共通の YAML frontmatter

```yaml
---
type: <type>                # 下記から選択
id: <仮名ID>                # person 等で必要
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - <カテゴリタグ>
  - <汎用タグ>
cssclasses:                  # 層別配色
  - layer-<layer>
status: active | archived | pending-amendment | under-review
---
```

### type 値（welfare-graph 固有 — data-wiki の entity/concept とは別系統）

| type | 配置層 | 用途 |
|---|---|---|
| `law` | 60_Laws | 法令 |
| `guideline` | 61_Guidelines | 厚労省ガイドライン |
| `framework` | 62_Frameworks | 理論フレームワーク |
| `disorder` | 63_Disorders | 障害特性 |
| `method` | 64_Methods | 支援技法 |
| `assessment` | 65_Assessments | アセスメントツール |
| `service` | 66_Services | 障害福祉サービス |
| `org` | 67_Orgs | 関係機関 |
| `person` | 10_People | 利用者（プライベート層） |
| `episode` | 20_Episodes | エピソード（プライベート層） |
| `insight` | 30_Insights | 抽象化知見 |
| `stakeholder` | 40_Stakeholders | 関係者（プライベート層） |
| `care-role` / `substitute` / `simulation` | 50_Resilience | 親亡き後設計（プライベート層） |
| `moc` | 00_MOC | Map of Content |
| `meta` | 90_Meta | 運用設計 |

### 改正追随フィールド（law / guideline / service 必須）

```yaml
source_url: "https://..."
monitoring_url: "..."
version: "令和6年改正"
version_hash: "..."
effective_date: YYYY-MM-DD
review_due: YYYY-MM-DD
last_verified: YYYY-MM-DD
amendment_history: [...]
```

### relations（重み付きリンク）

```yaml
relations:
  - to: "[[60_Laws/障害者総合支援法]]"
    type: applies-to              # type 辞書は [[90_Meta/SCHEMA]] §4 参照
    weight: 0.9                   # 0.0-1.0
    evidence: "5条"
    rationale: "..."
```

### 本文規約

- `# タイトル` は先頭に 1 つのみ。本文見出しは `##` から開始
- 内部リンクは `[[<層>/<ファイル名>]]` 形式（例: `[[60_Laws/障害者総合支援法]]`）
- 仮名 ID への参照は `[[P-0001]]` で可（短縮形解決される）
- 引用は `> [!quote]` コールアウト（§8）
- 矛盾・注意事項は `> [!warning]` コールアウト（§8）
- 出典は本文末尾の `## 出典` セクションに明記

詳細仕様: [`90_Meta/SCHEMA.md`](90_Meta/SCHEMA.md)

---

## §5 改正追随（welfare-graph 固有）

障害福祉の法令・ガイドライン・サービス報酬は定期的に改正される。welfare-graph は **進化する知識グラフ** として 4 層で追随する:

1. **検知層**: `amendment_check.py` が review_due / version_hash / monitoring_url を監視
2. **差分層**: 旧版を `60_Laws/archived/` 等に退避し `supersedes` チェーンで繋ぐ
3. **統合層**: `law-amendment-integrate` スキルが diff を取り込み relations を再評価
4. **通知層**: `vault_health_check` の CRITICAL + GitHub Actions 月次 Issue 起票

詳細運用: [`90_Meta/amendment-tracking.md`](90_Meta/amendment-tracking.md)

---

## §6 ドメインタグ体系

[`90_Meta/taxonomy.md`](90_Meta/taxonomy.md) 参照。

### 基本タグ（汎用）

`#障害福祉` `#知的障害` `#発達障害` `#精神障害` `#権利擁護` `#意思決定支援` `#虐待対応` `#親亡き後` `#性教育` `#成年後見` `#就労支援` `#相談支援` `#報酬改定` `#法改正`

### 層タグ（必須）

各ノートに 1 個、層を示すタグ: `law` / `guideline` / `framework` / `disorder` / `method` / `assessment` / `service` / `org` / `person` / `insight` 等

### 改正対応タグ

`令和6改正` / `令和9改正` / `archived` / `pending-amendment` / `新設` / `廃止` 等

新規タグ追加は `90_Meta/taxonomy.md` を更新してから使用。

---

## §7 個人情報の匿名化ルール

| 情報種別 | 処理 |
|---|---|
| 氏名（当事者） | `P-XXXX`（Person） |
| 家族 | `F-XXXX`（Family） |
| 事業所 | `O-XXXX`（Office） |
| 医療機関 | `M-XXXX`（Medical） |
| 成年後見人 | `G-XXXX`（Guardian） |
| 社会福祉協議会 | `S-XXXX` |
| 相談支援専門員 | `C-XXXX`（Consultant） |
| その他 | `N-XXXX`（Neighbor 他） |
| 電話番号 | 完全削除 |
| メール | 完全削除 |
| 住所 | 「都市部」「地方自治体」等に抽象化 |
| 日付（事件特定性あり） | 「2020年代前半」等に粒度を下げる |
| 生年月日 | 年齢層（「40 代」）に変換 |

### 機密ファイル

- `90_Meta/alias_map.md`: 仮名↔実名対応表。**必ず Meld Encrypt プラグインで暗号化**
- 原本（.md）は `.gitignore` で除外、暗号化版（.md.mdenc）のみコミット可

### 自動検知

- `.claude/hooks/realname_detect.py` が PreToolUse フックで書き込み時に検査
- 漢字フルネーム・カタカナフルネーム・電話番号パターンを検出
- 意図的な例示には `<!-- allow-realname -->` マーカーで許可

---

## §8 Obsidian コールアウト規約

Obsidian のコールアウト（`> [!type]`）を以下のように使い分ける:

| コールアウト | 用途 | 例 |
|---|---|---|
| `> [!warning]` | 矛盾・改正予告・重大注意 | `> [!warning] 令和9年改正で変更予定` |
| `> [!quote]` | 一次資料からの引用 | `> [!quote] 障害者総合支援法 5条` |
| `> [!info]` | 補足・参考情報 | `> [!info] 実務では...` |
| `> [!note]` | メモ・気付き | `> [!note] この条文は...` |
| `> [!tip]` | 運用上のヒント | `> [!tip] 区分認定時は...` |
| `> [!danger]` | 法的リスク・禁忌 | `> [!danger] 身体拘束は...` |
| `> [!example]` | 具体例 | `> [!example] 20 代男性...` |
| `> [!success]` | 合意・決着 | `> [!success] 令和6年改正で確定` |

### 使い方の原則

- **矛盾は必ず `> [!warning]`** で明示。勝手に正誤判断しない
- **引用は `> [!quote]`** で出典明記（条文番号・ページ）
- **断定を避ける語尾と併用**: 「〜と考えられる」「〜の可能性が高い」

---

## §9 会話保存モード（save）

ユーザーが以下のように指示した場合に起動:
- 「この会話を wiki に保存して」
- 「このチャットを welfare-graph に」
- 「今の議論を記録して」

### 手順

1. **会話の構造化**: 現在の会話から以下を抽出
   - トピック（1 行タイトル）
   - 背景・経緯
   - 議論の要点（箇条書き）
   - 決定事項・結論
   - 未解決事項・次のアクション
   - 関連する既存ノート（`[[...]]` リンク）

2. **`raw/notes/` に保存**: ファイル名は `YYYY-MM-DD_トピック名.md`

   ```yaml
   ---
   type: conversation
   date: YYYY-MM-DD
   source: claude.ai  # または claude-desktop / claude-code
   participants: [河原, Claude]
   tags: [raw, notes, conversation]
   ---
   ```

3. **個人情報の匿名化**: §7 のルールを適用

4. **log.md に追記**: 保存実施を記録

5. **ingest への接続**: 保存後「このまま Wiki に統合（ingest）しますか？」と確認
   - yes → ingest モード（`raw-to-wiki` スキル）に移行
   - no → raw/notes/ への保存のみで完了

### 抽出ルール

- コードブロック・コマンド出力は要約し、本質的な判断・理由を残す
- 試行錯誤の過程は省略し、最終結論と根拠を記録する
- 会話の「流れ」より「知見」を優先して構造化する
- 個人情報（§7）は匿名化

詳細: [`.claude/skills/conversation-save/SKILL.md`](.claude/skills/conversation-save/SKILL.md)

---

## §10 他システム連携

### Neo4j（welfare-graph 固有 DB）

- 起動: `docker run -d --name neo4j-skillgraph ...`
- 同期: `python3 90_Meta/scripts/sync_to_neo4j.py`
- 実用クエリ集: [`90_Meta/neo4j-queries.md`](90_Meta/neo4j-queries.md)
- 設計: [`90_Meta/neo4j-integration-design.md`](90_Meta/neo4j-integration-design.md)

Wiki ページから Neo4j ノードへの参照は frontmatter の `nid` プロパティが自動的にパスベース ID として保存される。

### MCP サーバー

Claude Desktop / Code / Cursor 等の MCP クライアントから vault を照会。

- 提供 Tools: 10 種（search_vault / support_hypothesis 等）
- プライバシー: プライベート層は MCP 経由で公開しない
- セットアップ: [`docs/MCP_SETUP.md`](docs/MCP_SETUP.md)

### data-wiki との関係

本プロジェクトは `~/Obsidian/data-wiki/CLAUDE.md` の LLM Wiki パターンに着想を得ている。両者は **独立プロジェクト** で、目的が異なる:

- **data-wiki**: 多領域（福祉法・民事訴訟法等）の抽象 entity/concept Wiki
- **welfare-graph**: 障害福祉特化の 9 層ドメインアーキテクチャ

data-wiki 側の資料を welfare-graph に取り込む場合は ingest モードで変換（匿名化方式の相違に注意）。

---

## §11 スクリプト

| スクリプト | 用途 | 実行方法 |
|---|---|---|
| `90_Meta/scripts/vault_health_check.py` | 健全性診断 | `python3 90_Meta/scripts/vault_health_check.py` |
| `90_Meta/scripts/amendment_check.py` | 改正追随チェック | `python3 90_Meta/scripts/amendment_check.py [--online]` |
| `90_Meta/scripts/sync_to_neo4j.py` | Neo4j 同期 | `python3 90_Meta/scripts/sync_to_neo4j.py` |
| `90_Meta/scripts/add_cssclasses.py` | CSS クラス一括追加 | `python3 90_Meta/scripts/add_cssclasses.py` |
| `90_Meta/scripts/generate_overview.py` | overview.md 生成 | `python3 90_Meta/scripts/generate_overview.py` |

スクリプトは vault root をカレントディレクトリとして実行すること。

---

## §12 現在の Wiki 統計

`overview.md` が自動生成する最新値を参照。以下は執筆時点のスナップショット:

| 層 | ページ数 |
|---|---|
| 60_Laws（法令） | 11（+ archived 1） |
| 61_Guidelines（ガイドライン） | 11 |
| 62_Frameworks（理論） | 7 |
| 63_Disorders（障害特性） | 12 |
| 64_Methods（支援技法） | 13 |
| 65_Assessments（アセスメント） | 9 |
| 66_Services（サービス） | 21 |
| 67_Orgs（関係機関） | 13 |
| 30_Insights（知見） | 5 |
| 00_MOC | 7 |
| 90_Meta | 5 |
| **合計（公開層）** | **120** |
| **relations 総数** | **355** |

最終更新: `overview.md` を参照。

---

## §13 本マニュアルの改訂

- 2026-04-20: 初版（data-wiki/CLAUDE.md §1-§10 の構造を踏襲）
