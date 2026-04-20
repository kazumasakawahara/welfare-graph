"""welfare-graph MCP server.

stdio で動作する MCP サーバー。Claude Desktop / Code 等のクライアントから
障害福祉知識グラフを照会するためのツール・リソース・プロンプトを提供。
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from . import __version__
from .domain import (
    check_amendment_status,
    find_applicable_laws,
    find_methods_for_disorder,
    find_services_for_profile,
)
from .hypothesis import generate_hypothesis
from .search import search_vault
from .traverse import bfs_traverse, get_neighbors
from .vault import Vault, load_vault_from_env

logger = logging.getLogger("welfare-graph-mcp")

# 起動時に vault を一度だけロード
_vault: Vault | None = None


def get_vault() -> Vault:
    global _vault
    if _vault is None:
        _vault = load_vault_from_env()
    return _vault


# ───────────────────────────────────────────────────────────────────
# シリアライザ
# ───────────────────────────────────────────────────────────────────

def note_to_dict(note, include_content: bool = False) -> dict[str, Any]:
    """Note を辞書化."""
    d = {
        "nid": note.nid,
        "title": note.title,
        "layer": note.layer,
        "type": note.metadata.get("type", ""),
        "rel_path": note.rel_path,
        "status": note.metadata.get("status", "active"),
        "version": note.metadata.get("version"),
        "effective_date": str(note.metadata.get("effective_date", "")),
        "review_due": str(note.metadata.get("review_due", "")),
        "source_url": note.metadata.get("source_url"),
        "tags": note.metadata.get("tags", []),
        "archived": note.archived,
    }
    if include_content:
        d["content"] = note.content
        d["frontmatter"] = {
            k: (str(v) if hasattr(v, "isoformat") else v)
            for k, v in note.metadata.items()
            if k != "relations"
        }
        d["relations"] = note.relations
    return d


def hits_to_text(hits, max_results: int = 10) -> str:
    """検索結果を表示用テキストに整形."""
    if not hits:
        return "該当なし"
    lines = []
    for i, hit in enumerate(hits[:max_results], 1):
        n = hit.note
        lines.append(f"## {i}. [{n.layer}] {n.title}")
        lines.append(f"   nid: `{n.nid}`")
        lines.append(f"   type: {n.metadata.get('type', '?')} / score: {hit.score:.1f}")
        lines.append(f"   matched: {', '.join(hit.matched_fields)}")
        if n.metadata.get("source_url"):
            lines.append(f"   source: {n.metadata['source_url']}")
        if hit.snippet:
            lines.append(f"   snippet: {hit.snippet}")
        lines.append("")
    return "\n".join(lines)


def notes_to_text(notes, label: str = "結果") -> str:
    if not notes:
        return f"{label}: 該当なし"
    lines = [f"## {label}（{len(notes)}件）", ""]
    for i, n in enumerate(notes, 1):
        status_marker = ""
        if n.metadata.get("status") == "pending-amendment":
            status_marker = " ⚠ 改正予告中"
        elif n.archived:
            status_marker = " 📦 archived"
        lines.append(f"{i}. **{n.title}**{status_marker}")
        lines.append(f"   - `{n.nid}` (layer: {n.layer})")
        if n.metadata.get("source_url"):
            lines.append(f"   - source: {n.metadata['source_url']}")
    return "\n".join(lines)


# ───────────────────────────────────────────────────────────────────
# MCP Server
# ───────────────────────────────────────────────────────────────────

server = Server("welfare-graph")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_vault",
            description=(
                "welfare-graph 知識ノートをキーワードで横断検索する。"
                "障害福祉の法令・ガイドライン・サービス・障害特性・支援技法等の知識を含む。"
                "クエリは日本語可。layer や type で絞り込み可。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索クエリ（日本語可、空白区切り）"},
                    "layer": {
                        "type": "string",
                        "description": "絞り込み層（60_Laws / 61_Guidelines / 62_Frameworks / 63_Disorders / 64_Methods / 65_Assessments / 66_Services / 67_Orgs / 30_Insights / 00_MOC）",
                    },
                    "node_type": {
                        "type": "string",
                        "description": "絞り込み type（law / guideline / service / disorder / method 等）",
                    },
                    "include_archived": {
                        "type": "boolean",
                        "description": "archived ノートを含めるか（デフォルト false）",
                        "default": False,
                    },
                    "limit": {"type": "integer", "description": "最大結果数", "default": 10},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_note",
            description="指定 nid のノート全文（frontmatter + content + relations）を取得",
            inputSchema={
                "type": "object",
                "properties": {
                    "nid": {
                        "type": "string",
                        "description": "ノード ID（例: '60_Laws/障害者総合支援法'）または短縮名",
                    },
                },
                "required": ["nid"],
            },
        ),
        Tool(
            name="get_related",
            description=(
                "指定ノードのグラフ近傍を BFS で探索。"
                "applies-to / responds-to / mandated-by 等の関係を辿って関連知識を集める。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "nid": {"type": "string", "description": "起点ノード ID"},
                    "max_depth": {"type": "integer", "description": "最大ホップ数", "default": 2},
                    "rel_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "フィルタする relation type（省略時は全て）",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["out", "in", "both"],
                        "default": "both",
                    },
                    "target_layers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "結果に含める層",
                    },
                    "min_weight": {"type": "number", "description": "weight 下限", "default": 0.0},
                },
                "required": ["nid"],
            },
        ),
        Tool(
            name="find_applicable_laws",
            description=(
                "状況記述から適用される可能性が高い法令・ガイドラインを抽出。"
                "例: 『虐待の疑いがある』『成年後見について相談したい』等の状況を入力。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "situation": {"type": "string", "description": "状況記述（日本語）"},
                },
                "required": ["situation"],
            },
        ),
        Tool(
            name="find_methods_for_disorder",
            description=(
                "障害特性名から、エビデンスに基づく支援技法（responds-to）と禁忌技法（contraindicated）を抽出。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "disorder_name": {
                        "type": "string",
                        "description": "障害特性名（例: '自閉スペクトラム症' '強度行動障害'）",
                    },
                },
                "required": ["disorder_name"],
            },
        ),
        Tool(
            name="find_services_for_profile",
            description=(
                "障害特性・キーワードから利用可能な障害福祉サービスを探索。"
                "障害層からサービス層へのグラフ探索 + キーワード検索を併用。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "disorders": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "障害特性名のリスト",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "追加キーワード（例: ['就労', '通所']）",
                    },
                },
            },
        ),
        Tool(
            name="support_hypothesis",
            description=(
                "利用者プロファイル（自由記述）から 4 レンズ（法令適合・サービス適格・技法マッチング・類似事例）"
                "で支援仮説を生成。免責事項・次のアクション付き。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_text": {
                        "type": "string",
                        "description": "利用者の状況記述（年齢・診断・生活状況・希望等）",
                    },
                    "disorders": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "既知の障害特性（明示指定）",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "追加キーワード",
                    },
                },
                "required": ["profile_text"],
            },
        ),
        Tool(
            name="check_amendment_status",
            description=(
                "改正追随の状況サマリ。期限超過・期限近接・pending-amendment 中のノードを一覧化。"
                "回答に『最新情報注意』を付ける根拠として使う。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "対象層（60_Laws / 61_Guidelines / 66_Services）。省略で全て",
                    },
                },
            },
        ),
        Tool(
            name="list_layer",
            description="指定層の全ノート一覧を返す（俯瞰用）",
            inputSchema={
                "type": "object",
                "properties": {
                    "layer": {
                        "type": "string",
                        "description": "層名（例: '63_Disorders' '66_Services'）",
                    },
                    "include_archived": {"type": "boolean", "default": False},
                },
                "required": ["layer"],
            },
        ),
        Tool(
            name="vault_stats",
            description="vault 全体統計（ノード数・層別件数・関係数）を取得",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    vault = get_vault()
    args = arguments or {}

    try:
        if name == "search_vault":
            hits = search_vault(
                vault,
                query=args["query"],
                layer=args.get("layer"),
                node_type=args.get("node_type"),
                include_archived=args.get("include_archived", False),
                limit=args.get("limit", 10),
            )
            text = f"検索クエリ: {args['query']}\n結果: {len(hits)} 件\n\n" + hits_to_text(hits)
            return [TextContent(type="text", text=text)]

        elif name == "get_note":
            note = vault.get(args["nid"])
            if not note:
                return [TextContent(type="text", text=f"ノートが見つかりません: {args['nid']}")]
            d = note_to_dict(note, include_content=True)
            return [TextContent(type="text", text=json.dumps(d, ensure_ascii=False, indent=2))]

        elif name == "get_related":
            nodes = bfs_traverse(
                vault,
                start_nid=args["nid"],
                max_depth=args.get("max_depth", 2),
                rel_types=args.get("rel_types"),
                direction=args.get("direction", "both"),
                target_layers=args.get("target_layers"),
                min_weight=args.get("min_weight", 0.0),
            )
            if not nodes:
                return [TextContent(type="text", text=f"近傍なし（起点: {args['nid']}）")]
            lines = [f"## 起点: {args['nid']} の近傍 ({len(nodes)} 件)\n"]
            for tn in nodes:
                if tn.depth == 0:
                    continue
                via = " → ".join(f"[{e.rel_type} w={e.weight:.2f}]" for e in tn.via)
                lines.append(f"- (depth={tn.depth}) **{tn.note.title}** `{tn.note.nid}`")
                lines.append(f"  {via}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "find_applicable_laws":
            result = find_applicable_laws(vault, args["situation"])
            text = f"## 状況: {args['situation']}\n\n"
            text += "### 推論プロセス\n" + "\n".join(f"- {r}" for r in result.rationale) + "\n\n"
            text += notes_to_text(result.primary, "主要該当法令・ガイドライン") + "\n\n"
            text += notes_to_text(result.related, "関連法令・ガイドライン")
            return [TextContent(type="text", text=text)]

        elif name == "find_methods_for_disorder":
            result = find_methods_for_disorder(vault, args["disorder_name"])
            text = f"## 障害特性: {args['disorder_name']}\n\n"
            text += "### 推論プロセス\n" + "\n".join(f"- {r}" for r in result.rationale) + "\n\n"
            text += notes_to_text(result.primary, "適応する支援技法（responds-to）") + "\n\n"
            text += notes_to_text(result.related, "禁忌技法・併存障害")
            return [TextContent(type="text", text=text)]

        elif name == "find_services_for_profile":
            result = find_services_for_profile(
                vault,
                disorders=args.get("disorders"),
                keywords=args.get("keywords"),
            )
            text = "## サービス探索結果\n\n"
            text += "### 推論プロセス\n" + "\n".join(f"- {r}" for r in result.rationale) + "\n\n"
            text += notes_to_text(result.primary, "候補サービス") + "\n\n"
            text += notes_to_text(result.related, "提供機関")
            return [TextContent(type="text", text=text)]

        elif name == "support_hypothesis":
            h = generate_hypothesis(
                vault,
                profile_text=args["profile_text"],
                disorders=args.get("disorders"),
                keywords=args.get("keywords"),
            )
            lines = [f"# 支援仮説\n", f"## プロファイル要約\n{h.profile_summary}\n"]
            for lens in h.lenses:
                lines.append(f"\n## 🔍 {lens.name}")
                if lens.notes:
                    lines.append("### 推論")
                    for n in lens.notes:
                        lines.append(f"- {n}")
                lines.append(notes_to_text(lens.findings, "結果"))
            lines.append("\n## ⚠ 免責事項")
            for d in h.disclaimers:
                lines.append(f"- {d}")
            lines.append("\n## ➡ 次のアクション")
            for s in h.next_steps:
                lines.append(f"- {s}")
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "check_amendment_status":
            status = check_amendment_status(vault, args.get("domain"))
            return [TextContent(type="text", text=json.dumps(status, ensure_ascii=False, indent=2))]

        elif name == "list_layer":
            layer = args["layer"]
            include_archived = args.get("include_archived", False)
            notes = vault.list_layer(layer)
            if not include_archived:
                notes = [n for n in notes if not n.archived]
            return [TextContent(type="text", text=notes_to_text(notes, f"{layer} 一覧"))]

        elif name == "vault_stats":
            stats = vault.stats()
            return [TextContent(type="text", text=json.dumps(stats, ensure_ascii=False, indent=2))]

        else:
            return [TextContent(type="text", text=f"未知のツール: {name}")]

    except Exception as e:
        logger.exception("Tool error")
        return [TextContent(type="text", text=f"エラー: {type(e).__name__}: {e}")]


# ───────────────────────────────────────────────────────────────────
# Resources
# ───────────────────────────────────────────────────────────────────

@server.list_resources()
async def list_resources() -> list[Resource]:
    vault = get_vault()
    resources: list[Resource] = []

    # MOC ノートをリソース化
    for moc_note in vault.list_layer("00_MOC"):
        resources.append(Resource(
            uri=f"welfare-graph://moc/{moc_note.path.stem}",
            name=f"MOC: {moc_note.title}",
            description=f"Map of Content: {moc_note.title}",
            mimeType="text/markdown",
        ))

    # 主要メタ
    for meta_name in ("SCHEMA", "amendment-tracking", "neo4j-queries", "neo4j-integration-design"):
        path = vault.root / "90_Meta" / f"{meta_name}.md"
        if path.exists():
            resources.append(Resource(
                uri=f"welfare-graph://meta/{meta_name}",
                name=f"Meta: {meta_name}",
                description=f"運用設計: {meta_name}",
                mimeType="text/markdown",
            ))

    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    vault = get_vault()
    uri_str = str(uri)

    if uri_str.startswith("welfare-graph://moc/"):
        name = uri_str.removeprefix("welfare-graph://moc/")
        path = vault.root / "00_MOC" / f"{name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")

    if uri_str.startswith("welfare-graph://meta/"):
        name = uri_str.removeprefix("welfare-graph://meta/")
        path = vault.root / "90_Meta" / f"{name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")

    if uri_str.startswith("welfare-graph://note/"):
        nid = uri_str.removeprefix("welfare-graph://note/")
        note = vault.get(nid)
        if note:
            return note.path.read_text(encoding="utf-8")

    raise ValueError(f"Unknown resource URI: {uri_str}")


# ───────────────────────────────────────────────────────────────────
# Prompts
# ───────────────────────────────────────────────────────────────────

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="consult_for_person",
            description="当事者の状況に基づく支援相談（4レンズ仮説生成 + 法令確認）",
            arguments=[
                PromptArgument(
                    name="situation",
                    description="当事者の状況（年齢・診断・生活状況・困りごと）",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="check_legal_compliance",
            description="特定の支援場面における法令適合チェック",
            arguments=[
                PromptArgument(
                    name="scenario",
                    description="支援場面の記述",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="find_local_services",
            description="障害特性・希望に合うサービス候補を探索",
            arguments=[
                PromptArgument(
                    name="needs",
                    description="本人の希望・特性",
                    required=True,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    args = arguments or {}

    if name == "consult_for_person":
        situation = args.get("situation", "")
        text = (
            f"以下の当事者の状況について、welfare-graph の知識を活用して支援を検討してください。\n\n"
            f"## 状況\n{situation}\n\n"
            f"## 手順\n"
            f"1. `support_hypothesis` ツールで 4 レンズ仮説を生成\n"
            f"2. `find_applicable_laws` で関連法令を確認\n"
            f"3. `check_amendment_status` で最新情報の確認漏れがないか検証\n"
            f"4. 結果を統合し、免責事項・次のアクションを必ず添える\n"
            f"5. 個別判断は担当相談支援専門員の合議が必要であることを明示\n"
        )
        return GetPromptResult(
            description="当事者の状況に基づく支援相談",
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=text)),
            ],
        )

    if name == "check_legal_compliance":
        scenario = args.get("scenario", "")
        text = (
            f"以下の支援場面について、法令・ガイドライン適合性を確認してください。\n\n"
            f"## 場面\n{scenario}\n\n"
            f"## 手順\n"
            f"1. `find_applicable_laws` で適用法令を抽出\n"
            f"2. 各法令の `get_note` で詳細を確認\n"
            f"3. 義務（compliance-required, mandatory-report-trigger）を明示\n"
            f"4. `check_amendment_status` で改正動向を確認\n"
        )
        return GetPromptResult(
            description="法令適合性チェック",
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=text)),
            ],
        )

    if name == "find_local_services":
        needs = args.get("needs", "")
        text = (
            f"以下のニーズに合うサービスを探索してください。\n\n"
            f"## ニーズ\n{needs}\n\n"
            f"## 手順\n"
            f"1. `find_services_for_profile` で候補サービスを抽出\n"
            f"2. 各サービスの `get_note` で利用要件・支給量を確認\n"
            f"3. 提供機関（67_Orgs）の確認\n"
            f"4. 利用者の意思決定支援を最優先する旨を明示\n"
        )
        return GetPromptResult(
            description="サービス探索",
            messages=[
                PromptMessage(role="user", content=TextContent(type="text", text=text)),
            ],
        )

    raise ValueError(f"Unknown prompt: {name}")


# ───────────────────────────────────────────────────────────────────
# エントリポイント
# ───────────────────────────────────────────────────────────────────

async def _run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
    )
    logger.info(f"welfare-graph-mcp v{__version__} 起動中...")
    try:
        v = get_vault()
        logger.info(f"vault: {v.root} ({len(v.notes)} ノート / {sum(len(rs) for rs in v.outgoing.values())} 関係)")
    except Exception as e:
        logger.error(f"vault ロード失敗: {e}")
        sys.exit(1)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """CLI エントリポイント."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
