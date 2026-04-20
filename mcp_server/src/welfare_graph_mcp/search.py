"""キーワード検索モジュール.

Vault 内ノートを title / tags / 本文 / frontmatter フィールドから検索し、
スコア順に返す。シンプルな TF + フィールド重み方式。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .vault import Note, Vault


# フィールド別スコア重み
FIELD_WEIGHTS = {
    "title": 5.0,
    "name": 4.0,
    "tags": 3.0,
    "frontmatter": 2.0,
    "content": 1.0,
}


@dataclass
class SearchHit:
    note: Note
    score: float
    snippet: str
    matched_fields: list[str]


def _tokenize_query(query: str) -> list[str]:
    """クエリを単純トークン化（空白区切り + 日本語対応）."""
    # 空白で区切り、空文字列除去
    raw_tokens = re.split(r"[\s　,、。]+", query.strip())
    return [t.lower() for t in raw_tokens if t]


def _make_snippet(content: str, query_tokens: list[str], window: int = 80) -> str:
    """マッチ箇所周辺の snippet を生成."""
    if not content:
        return ""
    lower = content.lower()
    best_pos = -1
    for tok in query_tokens:
        pos = lower.find(tok)
        if pos >= 0 and (best_pos == -1 or pos < best_pos):
            best_pos = pos
    if best_pos < 0:
        return content[: window * 2].replace("\n", " ").strip()
    start = max(0, best_pos - window)
    end = min(len(content), best_pos + window)
    snippet = content[start:end].replace("\n", " ").strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(content):
        snippet = snippet + "…"
    return snippet


def _score_note(note: Note, query_tokens: list[str]) -> tuple[float, list[str]]:
    """単一ノートの検索スコアを算出."""
    if not query_tokens:
        return 0.0, []

    score = 0.0
    matched: list[str] = []

    # title マッチ
    title_lower = note.title.lower()
    for tok in query_tokens:
        if tok in title_lower:
            score += FIELD_WEIGHTS["title"]
            if "title" not in matched:
                matched.append("title")

    # name マッチ（ファイル名）
    name = note.path.stem.lower()
    for tok in query_tokens:
        if tok in name:
            score += FIELD_WEIGHTS["name"]
            if "name" not in matched:
                matched.append("name")

    # tags マッチ
    tags = note.metadata.get("tags") or []
    if isinstance(tags, list):
        tag_str = " ".join(str(t).lower() for t in tags)
        for tok in query_tokens:
            if tok in tag_str:
                score += FIELD_WEIGHTS["tags"]
                if "tags" not in matched:
                    matched.append("tags")

    # frontmatter 主要フィールドマッチ
    fm_searchable_keys = [
        "law_name", "guideline_name", "service_name", "disorder_name",
        "method_name", "framework_name", "assessment_name", "short_name",
        "summary", "issuer", "purpose", "target", "law_basis",
    ]
    for k in fm_searchable_keys:
        v = note.metadata.get(k)
        if not v:
            continue
        v_str = str(v).lower()
        for tok in query_tokens:
            if tok in v_str:
                score += FIELD_WEIGHTS["frontmatter"]
                if "frontmatter" not in matched:
                    matched.append("frontmatter")

    # content マッチ
    content_lower = note.content.lower()
    for tok in query_tokens:
        cnt = content_lower.count(tok)
        if cnt > 0:
            score += FIELD_WEIGHTS["content"] * min(cnt, 5)  # 上限を設ける
            if "content" not in matched:
                matched.append("content")

    return score, matched


def search_vault(
    vault: Vault,
    query: str,
    layer: str | None = None,
    node_type: str | None = None,
    include_archived: bool = False,
    limit: int = 10,
) -> list[SearchHit]:
    """vault を検索.

    Args:
        query: 検索クエリ（空白区切り）
        layer: 絞り込み層（例: "60_Laws"）
        node_type: 絞り込み type（例: "law"）
        include_archived: archived ノートを含めるか
        limit: 最大結果数

    Returns:
        スコア順の SearchHit リスト
    """
    tokens = _tokenize_query(query)
    if not tokens:
        return []

    candidates: list[Note] = []
    if layer:
        candidates = vault.list_layer(layer)
    elif node_type:
        candidates = vault.list_type(node_type)
    else:
        candidates = list(vault.notes.values())

    if not include_archived:
        candidates = [n for n in candidates if not n.archived]

    hits: list[SearchHit] = []
    for note in candidates:
        score, matched = _score_note(note, tokens)
        if score <= 0:
            continue
        snippet = _make_snippet(note.content, tokens)
        hits.append(SearchHit(note=note, score=score, snippet=snippet, matched_fields=matched))

    hits.sort(key=lambda h: -h.score)
    return hits[:limit]
