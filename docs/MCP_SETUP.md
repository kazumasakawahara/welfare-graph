<!-- allow-realname -->
# welfare-graph MCP サーバー セットアップガイド

Claude Desktop / Claude Code / Cursor などの MCP クライアントから welfare-graph 知識グラフを照会できるようにする手順書。

## 📖 このガイドで何ができるようになるか

- Claude Desktop に「強度行動障害の支援方法は？」と聞くと、**welfare-graph の知識ベース** を使った根拠付きの回答が得られる
- 「親が高齢になってきた」「虐待の疑い」など、相談支援領域の質問に **法令の出典付き** で答える
- 改正動向を踏まえた「最新確認が必要」アラートも自動で付く

## 🛠️ 必要なもの

- Python 3.10 以上（推奨: 3.12 以上）
- 以下のいずれか
  - **uv**（推奨）: https://docs.astral.sh/uv/
  - **pipx**: https://pipx.pypa.io/
  - 一般的な `pip` でも可
- MCP クライアント（Claude Desktop / Claude Code 等）
- welfare-graph リポジトリの clone（vault 本体）

## 📦 インストール

### 方法 A: uv tool（推奨・最も簡単）

```bash
# 1. uv をインストール（未インストールなら）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. welfare-graph を clone
git clone https://github.com/kazumasakawahara/welfare-graph.git
cd welfare-graph

# 3. MCP サーバーをインストール
uv tool install --from ./mcp_server welfare-graph-mcp
```

これで `welfare-graph-mcp` コマンドがどこからでも実行可能になります。

### 方法 B: pipx

```bash
git clone https://github.com/kazumasakawahara/welfare-graph.git
cd welfare-graph
pipx install ./mcp_server
```

### 方法 C: pip + venv（手動管理）

```bash
git clone https://github.com/kazumasakawahara/welfare-graph.git
cd welfare-graph

python3 -m venv .venv
source .venv/bin/activate
pip install -e ./mcp_server
```

この場合は MCP 設定の `command` を venv 内 Python のフルパスにする必要があります。

## ⚙️ MCP クライアント設定

### Claude Desktop

設定ファイル: `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）

存在しない場合は新規作成:

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/Users/YOUR_NAME/path/to/welfare-graph"
      }
    }
  }
}
```

**重要**: `WELFARE_GRAPH_VAULT` は **vault 本体の絶対パス**（`60_Laws/` 等が直下にあるディレクトリ）。

設定後、Claude Desktop を **完全終了 → 再起動**。

### Claude Code（CLI）

設定ファイル（プロジェクト内）: `.claude/settings.json`

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/Users/YOUR_NAME/path/to/welfare-graph"
      }
    }
  }
}
```

ユーザー全体（グローバル）に設定したい場合: `~/.claude/settings.json`

### Cursor

設定ファイル: `~/.cursor/mcp.json`（または Cursor 設定 → MCP）

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/Users/YOUR_NAME/path/to/welfare-graph"
      }
    }
  }
}
```

### Windows の場合

`command` は同じ `welfare-graph-mcp`（uv tool / pipx で PATH 通る）。
`WELFARE_GRAPH_VAULT` は Windows パス形式:

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "C:\\Users\\YOUR_NAME\\Documents\\welfare-graph"
      }
    }
  }
}
```

設定パス:
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`

## 🎓 グローバル Skill の登録（推奨）

MCP サーバーを「いつでも障害福祉の相談で使う」ようにするため、Skill を登録します。

### Claude Desktop / Code 共通

```bash
# ユーザー全体の skills ディレクトリにコピー
mkdir -p ~/.claude/skills/welfare-graph-consult
cp mcp_server/skill_templates/welfare-graph-consult/SKILL.md ~/.claude/skills/welfare-graph-consult/
```

これで「強度行動障害の支援方法は？」のような質問が来たとき、Claude が自動で welfare-graph MCP を起動して回答するようになります。

## ✅ 動作確認

### Claude Desktop で確認

設定後、Claude Desktop で新しい会話を開始し:

```
strength behavior disorder の支援方法を welfare-graph で調べて
```

または日本語で:

```
welfare-graph を使って、自閉スペクトラム症に有効な支援技法を教えてください
```

回答に「welfare-graph の検索結果」「source URL」「免責事項」が含まれれば成功。

### CLI で直接確認

```bash
# vault stats を取得
WELFARE_GRAPH_VAULT=/path/to/welfare-graph welfare-graph-mcp <<< '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

JSON-RPC 応答が返れば起動 OK。

## 🔍 提供される機能

### Tools（10 種）

| Tool | 用途 |
|---|---|
| `search_vault` | キーワード横断検索 |
| `get_note` | 個別ノート全文取得 |
| `get_related` | グラフ近傍 BFS 探索 |
| `find_applicable_laws` | 状況→該当法令 |
| `find_methods_for_disorder` | 障害特性→支援技法 |
| `find_services_for_profile` | 障害特性→サービス候補 |
| `support_hypothesis` | 4 レンズ支援仮説 |
| `check_amendment_status` | 改正追随状況 |
| `list_layer` | 層別ノート一覧 |
| `vault_stats` | vault 統計 |

### Resources

`welfare-graph://moc/Home` 等の MOC ノートと `welfare-graph://meta/SCHEMA` 等の運用設計書を URI で参照可能。

### Prompts

- `consult_for_person`: 当事者の状況に基づく支援相談
- `check_legal_compliance`: 法令適合性チェック
- `find_local_services`: サービス探索

## 🔒 プライバシー設計

MCP サーバーは以下を **絶対に公開しません**:

- `10_People/` 利用者個別ノート（架空でも非公開）
- `20_Episodes/` エピソード記録
- `30_Insights/hypotheses/` 個別仮説
- `40_Stakeholders/` 関係者
- `50_Resilience/` 親亡き後設計
- `90_Meta/alias_map.md` 仮名対応表
- `raw/` 一次資料

公開対象は **抽象化された知識層**（60-67 + 30_Insights の汎用知見 + 00_MOC + 90_Meta の運用設計）のみ。

## 🐛 トラブルシューティング

### Q. Claude Desktop で MCP サーバーが認識されない

1. 設定ファイルの JSON 構文エラーがないか確認（`jq . config.json`）
2. `welfare-graph-mcp` コマンドが PATH 上にあるか: `which welfare-graph-mcp`
3. Claude Desktop を **完全に終了**（Cmd+Q / プロセス kill）してから再起動
4. Claude Desktop のログを確認: `~/Library/Logs/Claude/`

### Q. `WELFARE_GRAPH_VAULT 環境変数を設定してください` エラー

設定ファイル内で env が正しく設定されているか確認。絶対パスであること。

### Q. `vault パスが存在しません` エラー

パスが正確か確認。`60_Laws/` 等のディレクトリが直下にあるか:

```bash
ls /path/to/welfare-graph/60_Laws/
```

### Q. tool 呼び出し結果が空・少ない

vault 内容を更新したら MCP サーバーを再起動（Claude Desktop 再起動）。インメモリ index は起動時に構築されます。

### Q. uv tool install で失敗する

Python 3.10 以上が必要:

```bash
uv python install 3.12
uv tool install --python 3.12 --from ./mcp_server welfare-graph-mcp
```

### Q. アップデート方法

```bash
cd /path/to/welfare-graph
git pull
uv tool install --reinstall --from ./mcp_server welfare-graph-mcp
```

Claude Desktop も再起動。

## 🚀 高度な使い方

### Neo4j バックエンド使用（将来拡張）

現状の MCP サーバーは markdown 直読みですが、将来 Neo4j バックエンドモードを追加予定:

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/path/to/welfare-graph",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password"
      }
    }
  }
}
```

### 複数 vault 運用

たとえば事業所内向けの拡張版 vault を別管理する場合:

```json
{
  "mcpServers": {
    "welfare-graph-public": {
      "command": "welfare-graph-mcp",
      "env": { "WELFARE_GRAPH_VAULT": "/path/to/public/welfare-graph" }
    },
    "welfare-graph-internal": {
      "command": "welfare-graph-mcp",
      "env": { "WELFARE_GRAPH_VAULT": "/path/to/internal/welfare-graph" }
    }
  }
}
```

ツール名が衝突しないよう、Claude が自動でサーバー名 prefix を付与します。

## 📚 関連ドキュメント

- [`mcp_server/README.md`](../mcp_server/README.md) — MCP サーバー本体仕様
- [`mcp_server/skill_templates/welfare-graph-consult/SKILL.md`](../mcp_server/skill_templates/welfare-graph-consult/SKILL.md) — Skill 定義
- [`docs/USER_GUIDE.md`](USER_GUIDE.md) — vault 全体の使用説明書
- [`90_Meta/SCHEMA.md`](../90_Meta/SCHEMA.md) — frontmatter 仕様
- [`90_Meta/amendment-tracking.md`](../90_Meta/amendment-tracking.md) — 改正追随設計
