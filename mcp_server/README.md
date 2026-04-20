<!-- allow-realname -->
# welfare-graph MCP server

障害福祉知識グラフ [welfare-graph](../) を Claude Desktop / Code 等の MCP クライアントから照会可能にする MCP サーバー。

## 提供する Tools（10 種）

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
| `vault_stats` | vault 全体統計 |

## 提供する Resources

- `welfare-graph://moc/{Home, Knowledge, Sexuality, ...}`
- `welfare-graph://meta/{SCHEMA, amendment-tracking, neo4j-queries, ...}`
- `welfare-graph://note/{path}`

## 提供する Prompts

- `consult_for_person`: 当事者の状況に基づく支援相談ガイド
- `check_legal_compliance`: 法令適合性チェックガイド
- `find_local_services`: サービス探索ガイド

## インストール

```bash
# uv 推奨
uv tool install --from /path/to/welfare-graph/mcp_server welfare-graph-mcp

# pipx でも可
pipx install /path/to/welfare-graph/mcp_server
```

## 設定

### Claude Desktop（`~/Library/Application Support/Claude/claude_desktop_config.json`）

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/path/to/welfare-graph"
      }
    }
  }
}
```

### Claude Code（`~/.claude/settings.json` またはプロジェクト `.claude/settings.json`）

```json
{
  "mcpServers": {
    "welfare-graph": {
      "command": "welfare-graph-mcp",
      "env": {
        "WELFARE_GRAPH_VAULT": "/path/to/welfare-graph"
      }
    }
  }
}
```

## プライバシー設計

MCP 経由では公開しないディレクトリ・ファイル:

- `10_People/` 利用者個別ノート
- `20_Episodes/` エピソード記録
- `30_Insights/hypotheses/` 個別仮説
- `40_Stakeholders/` 関係者
- `50_Resilience/` 親亡き後設計
- `90_Meta/alias_map.md` 仮名→実名対応表
- `raw/` 一次資料（著作権配慮）

MCP 経由で公開対象となるのは **抽象化された知識層**（60-67 + 30_Insights の汎用知見 + 00_MOC + 90_Meta の運用設計）のみ。

## 詳細

[`docs/MCP_SETUP.md`](../docs/MCP_SETUP.md) を参照。
