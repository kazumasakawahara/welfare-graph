<!-- allow-realname -->
# welfare-graph

障害福祉分野の **計画相談専門員（相談支援専門員）** のための、
**Obsidian ベースの知識グラフ + Neo4j 分析基盤**。

計画相談業務で必要な **法令・ガイドライン・サービス・障害特性・支援技法・関係機関** を
重み付きリンクで繋ぎ、個別の利用者ノートから **根拠付きの支援仮説** を導けます。

## 👋 はじめての方へ

**Obsidian が初めて・プログラミング経験がない方も安心してください**。以下の順でお読みください:

- 🚀 **[15 分クイックスタート](docs/QUICKSTART.md)** — まず中身を見てみたい方向け
- 📖 **[使用説明書（全編）](docs/USER_GUIDE.md)** — 業務で本格的に使う方向け（17 章構成・約 1 時間で全機能習得）
- ❓ **[よくある質問（FAQ）](docs/FAQ.md)** — 困ったときの辞書
- 🤖 **[MCP セットアップ](docs/MCP_SETUP.md)** — Claude Desktop / Code から障害福祉相談に活用したい方向け

## 📐 特徴

- **9層アーキテクチャ**: 法令/ガイドライン/理論/障害特性/技法/アセスメント/サービス/機関/利用者
- **重み付きリンク**: `relations` に `type`（義務/推奨/禁忌 等）と `weight`（0-1）を付与
- **LLM-Wiki 方式**: 人が読む Obsidian Vault + 機械が辿る Neo4j グラフの二層構造
- **層別カラー**: CSS snippet + グラフ色分けで視認性向上
- **スキル群**: `support-hypothesis` / `vault-health-check` / `ecomap-from-relations` / `amendment-watch` / `law-amendment-integrate` 等
- **仮名化徹底**: 利用者情報は P-XXXX 等の仮名IDのみ、realname-detect フックで実名混入を自動ブロック
- **🆕 進化する知識グラフ**: 法令改正に追随する版管理機構（`archived/` + `amendment_history` + 月次 GitHub Actions 自動チェック）
- **🆕 MCP サーバー**: Claude Desktop / Claude Code / Cursor から障害福祉知識を直接照会可能（10 tools / 3 prompts / プライバシー保護設計）

## 📊 現在の規模

| 層 | ページ数 |
|---|---|
| 60_Laws（法令） | 9（+ archived 1） |
| 61_Guidelines（ガイドライン） | 10 |
| 62_Frameworks（理論） | 6 |
| 63_Disorders（障害特性） | 11 |
| 64_Methods（支援技法） | 12 |
| 65_Assessments（アセスメント） | 7 |
| 66_Services（サービス） | 18 |
| 67_Orgs（関係機関） | 12 |
| **Neo4j ノード** | **120+** |
| **Neo4j 関係** | **355+** |

## 🏗️ ディレクトリ構造

```
welfare-graph/
├── 00_MOC/                  ナビゲーション（Home / Knowledge / Sexuality 等）
├── 10_People/               利用者ノート（P-XXXX・全て架空）
├── 20_Episodes/             エピソード記録
├── 30_Insights/             抽象化された知見
│   └── hypotheses/          support-hypothesis の出力保存先
├── 40_Stakeholders/         具体関係者（仮名ID）
├── 50_Resilience/           親亡き後設計
│   ├── CareRoles/
│   ├── Simulations/
│   └── Substitutes/
├── 60_Laws/                 法令（総合支援法・虐待防止法・刑法性犯罪規定 等）
├── 61_Guidelines/           厚労省ガイドライン（意思決定支援GL・身体拘束適正化の手引 等）
├── 62_Frameworks/           理論（ICF・ストレングスモデル・PCP・TIC・SRHR・CSE）
├── 63_Disorders/            障害特性（知的・ASD・ADHD・統合失調症 等）
├── 64_Methods/              支援技法（構造化支援・ABA・CBT・CAP・性教育 等）
├── 65_Assessments/          アセスメント（区分認定・行動関連項目・Vineland-II 等）
├── 66_Services/             障害福祉サービス（居宅介護・生活介護・GH・計画相談 等）
├── 67_Orgs/                 関係機関（基幹相談支援C・児相・就ポツ・家裁 等）
├── 90_Meta/
│   ├── SCHEMA.md            frontmatter 仕様・リンク型辞書
│   ├── neo4j-integration-design.md
│   ├── SETUP_COLORS.md      彩色セットアップ手順
│   ├── templates/           ノートテンプレート
│   ├── scripts/             Python スクリプト
│   └── health-reports/      vault-health-check の出力
├── .claude/
│   ├── skills/              Claude Code スキル定義（6個）
│   └── hooks/               realname-detect 他
├── .obsidian/
│   ├── graph.json           グラフ色分け設定
│   ├── appearance.json
│   └── snippets/layer-colors.css
├── raw/                     一次資料（PDF は .gitignore で除外）
├── LICENSE                  MIT（コード）
├── LICENSE-DOCS             CC BY-SA 4.0（ドキュメント）
└── README.md                本ファイル
```

## 🚀 クイックスタート

### 必要な環境

- **Obsidian**（v1.5+ 推奨）
- **Python 3.9+**
- **Docker**（Neo4j 連携する場合）

### 初期セットアップ

```bash
# 1. クローン
git clone https://github.com/YOUR-USERNAME/welfare-graph.git
cd welfare-graph

# 2. Python 依存パッケージ
pip install neo4j python-frontmatter python-dotenv

# 3. 環境変数ファイル作成
cp .env.example .env
# .env を編集して Neo4j パスワードを設定

# 4. Obsidian で vault を開く
# Obsidian → 別の Vault を開く → welfare-graph フォルダを選択

# 5. CSS snippet を有効化（彩色）
# Obsidian 設定 → 外観 → CSS snippets → layer-colors を ON

# 6. Meld Encrypt プラグインをインストール（実名マップ暗号化用）
# 設定 → コミュニティプラグイン → Meld Encrypt
```

詳細な彩色セットアップ手順は [90_Meta/SETUP_COLORS.md](90_Meta/SETUP_COLORS.md) 参照。

### Neo4j 連携（オプション）

```bash
# Neo4j コンテナ起動
docker run -d \
  --name neo4j-welfare-graph \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/$(grep NEO4J_PASSWORD .env | cut -d= -f2) \
  -v neo4j-welfare-graph-data:/data \
  neo4j:5.26-community

# vault を Neo4j に同期
python3 90_Meta/scripts/sync_to_neo4j.py

# ブラウザで http://localhost:7474 を開いて探索
```

## 🛠️ 付属スクリプト・スキル

### Python スクリプト（`90_Meta/scripts/`）

- **`sync_to_neo4j.py`**: vault → Neo4j 同期（frontmatter relations + archived/ + supersedes 処理）
- **`vault_health_check.py`**: 全体品質診断（必須フィールド欠損・壊れリンク・孤児ノート等、archived 例外処理あり）
- **`amendment_check.py`**: 改正追随チェック（review_due 期限・version_hash ドリフト・pending-amendment 滞留検知）
- **`add_cssclasses.py`**: 新規ノートに frontmatter cssclasses を一括追加

### Claude Code スキル（`.claude/skills/`）

- **`support-hypothesis`**: 利用者の relations を4レンズで分析し根拠付き支援仮説を生成
- **`vault-health-check`**: 健全性診断レポート生成
- **`ecomap-from-relations`**: Mermaid エコマップを relations から自動生成
- **`visit-prep`**: 訪問前ブリーフィング生成
- **`monthly-summary`**: 月次モニタリングサマリ生成
- **`realname-check`**: 実名混入の定期監査
- **`raw-to-wiki`**: raw/ 一次資料 → 構造化 wiki ページへの変換
- **`amendment-watch`**: 法令改正情報の定期監視・status 更新提案
- **`law-amendment-integrate`**: 改正差分の取込・archived 退避・relations 再評価

## 📋 運用フロー（相談支援専門員向け）

1. **初回アセスメント**: `10_People/` に人物ノート作成、関係者を `40_Stakeholders/` に登録
2. **CareRole 棚卸し**: 親が担う機能を `50_Resilience/CareRoles/` に記録
3. **訪問後記録**: `20_Episodes/` にエピソード追加
4. **パターン抽出**: `30_Insights/` に知見として昇華
5. **支援仮説生成**: Claude Code から `support-hypothesis` スキルで4レンズ分析
6. **定期点検**: 月次で `vault-health-check` スキル実行

## 🔒 仮名化とセキュリティ

### 仮名ID体系

| 接頭辞 | 種別 |
|---|---|
| `P-XXXX` | 当事者（本人） |
| `F-XXXX` | 家族 |
| `O-XXXX` | 障害福祉サービス事業所 |
| `M-XXXX` | 医療機関 |
| `G-XXXX` | 成年後見人/保佐人/補助人 |
| `S-XXXX` | 社会福祉協議会（日生事業担当） |
| `C-XXXX` | 相談支援専門員 |
| `N-XXXX` | その他（近隣・民生委員等） |

実名↔仮名の対応表は `90_Meta/alias_map.md` で管理。**Meld Encrypt プラグインで暗号化** が必須。

### 実名混入防止

`.claude/hooks/realname_detect.py` が PreToolUse hook として動作し、書き込み時に
実名らしき文字列（漢字・カタカナフルネーム、電話番号）を検出してブロックします。

意図的な例示の場合はノート本文に `<!-- allow-realname -->` を挿入してください。

手動スキャン: `realname-check` スキルまたは `/realname-check` コマンド。

## 🎨 層別カラー

Obsidian の CSS snippet（`.obsidian/snippets/layer-colors.css`）で以下のように色分け:

| 層 | 色 |
|---|---|
| 60_Laws | 🟥 Red `#C62828` |
| 61_Guidelines | 🟧 Orange `#EF6C00` |
| 62_Frameworks | 🟪 Purple `#6A1B9A` |
| 63_Disorders | 🟨 Amber `#F9A825` |
| 64_Methods | 🟩 Green `#2E7D32` |
| 65_Assessments | 🟫 Brown `#5D4037` |
| 66_Services | 🟦 Blue `#1565C0` |
| 67_Orgs | 🟦 Teal `#00838F` |
| 10_People | ⚫ Blue-Gray `#455A64` |
| 00_MOC | ⭐ Gold `#FFA000` |

## 🤖 Claude Desktop / Code から照会する（MCP サーバー）

welfare-graph の知識を Claude Desktop / Claude Code / Cursor 等の任意の Claude セッションから直接照会できる MCP サーバーを同梱しています。

### 想定利用者

- 相談支援専門員（自分が業務中に AI に質問）
- 福祉系職員（業務知識の確認）
- 当事者・家族（基本知識の理解）
- 学生・研究者（教育・調査）

### インストール（1 行）

```bash
uv tool install --from ./mcp_server welfare-graph-mcp
```

### Claude Desktop 設定（`~/Library/Application Support/Claude/claude_desktop_config.json`）

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": { "WELFARE_GRAPH_VAULT": "/path/to/welfare-graph" }
    }
  }
}
```

### 提供される機能

| カテゴリ | 内容 |
|---|---|
| **Tools (10)** | search_vault / get_note / get_related / find_applicable_laws / find_methods_for_disorder / find_services_for_profile / support_hypothesis / check_amendment_status / list_layer / vault_stats |
| **Resources** | MOC 5 種、運用設計書 4 種、任意ノート |
| **Prompts (3)** | consult_for_person / check_legal_compliance / find_local_services |

### 使用例

Claude Desktop で以下のように質問:

```
「強度行動障害のある利用者への支援方法を welfare-graph で調べてください」
→ 厚労省研修テキスト、適応技法（構造化支援/ABA/PECS）、サービス選択肢、
  改正動向、注意事項、追加で必要な情報、免責事項を含む構造化された回答
```

### プライバシー設計

MCP 経由では `10_People/`・`20_Episodes/`・`alias_map.md` 等の個別情報は **絶対に公開しません**。公開対象は抽象化された知識層（60-67、30_Insights、00_MOC、90_Meta 設計書）のみ。

### グローバル Skill 登録（推奨）

```bash
mkdir -p ~/.claude/skills/welfare-graph-consult
cp mcp_server/skill_templates/welfare-graph-consult/SKILL.md ~/.claude/skills/welfare-graph-consult/
```

これで Claude が障害福祉相談を自動検知して MCP 起動します。

詳細: [`docs/MCP_SETUP.md`](docs/MCP_SETUP.md)

---

## 🌱 進化する知識グラフ（Evolving Knowledge Graph）

法令・ガイドライン・サービス報酬は改正されます。welfare-graph は **改正に追随する版管理機構** を組み込み、5 年後も使い続けられる知識グラフを目指しています（LLM-Wiki 思想の福祉適用）。

### 4 層アーキテクチャ

| 層 | 仕組み |
|---|---|
| **検知層** | `amendment_check.py` で `review_due` 期限 + `version_hash` ドリフト + 一次ソース監視 |
| **差分層** | 旧版を `archived/` に退避し `supersedes` チェーンで版を繋ぐ |
| **統合層** | `law-amendment-integrate` スキルが diff を取込・relations を再評価 |
| **通知層** | `vault_health_check` の CRITICAL 項目 + GitHub Actions 月次自動 Issue 起票 |

### 改正対応フィールド（frontmatter）

```yaml
version: "令和6年改正"
version_hash: "a3b4c5d6"        # 原文 SHA256 先頭8桁
effective_date: 2024-04-01
review_due: 2027-04-01
last_verified: 2026-04-20
status: active                  # active / pending-amendment / under-review / archived
monitoring_url: "https://..."
amendment_history:
  - version: "平成30年改正"
    effective_date: 2018-04-01
    summary: "..."
    archived_as: "[[archived/障害者総合支援法_H30]]"
supersedes: "[[archived/障害者総合支援法_H30]]"
```

詳細設計: [`90_Meta/amendment-tracking.md`](90_Meta/amendment-tracking.md)

### 自動化

- **GitHub Actions（月次）**: `.github/workflows/monthly-health-check.yml`
- **手動実行**: `python3 90_Meta/scripts/amendment_check.py --online`
- **Claude スキル**: `/amendment-watch`, `/law-amendment-integrate`

## 🤝 コントリビューション

本プロジェクトは相談支援専門員コミュニティの **共有知的資産** として、
無償で配布・改変・再配布可能です。

詳細は [`CONTRIBUTING.md`](CONTRIBUTING.md) 参照。

歓迎する貢献:

- **法令・ガイドラインの改定追従**（報酬改定年度等）→ Issue テンプレ「[AMENDMENT]」を活用
- **新規知識ノート**（難病・精神障害の各論・地域ごとの特殊事情）
- **Insight の追加**（現場で得た知見の匿名化・抽象化）
- **スキル・スクリプトの改良**
- **typo・表現の改善**

プルリクエスト時の注意:
1. **実名・個人情報は絶対に含めない**（hook が検知しますがダブルチェック）
2. **法的助言・医学的助言に誤認される表現を避ける**（「要検討」「担当相談員と協議」等の表現を使う）
3. **一次情報の出典** を frontmatter に明記（`source_url` / `version` / `effective_date` / `last_verified`）
4. **PR テンプレ** に従いチェックリストを完了

## ⚠️ 免責事項

- 本プロジェクトは **学習・参考・実務補助** を目的とします
- **法令・制度** は変更されます。最新情報は e-Gov・厚生労働省・自治体サイトで確認してください
- **個別ケースの判断** は担当相談支援専門員・医師・弁護士等の合議で行ってください
- LLM が生成する **支援仮説** は候補であり、採否は必ず人間が判断してください
- 利用者ノート（`P-XXXX`）は **すべて架空事例** です

## 📜 ライセンス

デュアルライセンス:

- **コード**（`.py` / `.css` / `.json` / スキル定義）: [MIT License](LICENSE)
- **ドキュメント**（Markdown ノート全般）: [CC BY-SA 4.0](LICENSE-DOCS)

両ライセンスとも、**商用利用を含む自由な使用・改変・再配布** を許可します。

## 🙏 謝辞

本プロジェクトは、日本全国の計画相談専門員・相談支援専門員の皆様の
日々の実践から学び、その業務を少しでも支える目的で公開されています。

現場の気付きや改善提案は Issue / Pull Request でお寄せください。

---

**🌱 相談支援専門員のためのオープンな知識グラフ。継続的に育てていきましょう。**
