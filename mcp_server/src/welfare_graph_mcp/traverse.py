"""グラフ traversal モジュール.

Vault の関係グラフ（outgoing / incoming）を多段で辿る。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .vault import Note, Vault


@dataclass
class RelationEdge:
    source_nid: str
    target_nid: str
    rel_type: str
    weight: float
    evidence: str
    direction: str  # "out" or "in"


@dataclass
class TraversalNode:
    note: Note
    depth: int
    via: list[RelationEdge]  # source からこのノードへの edge 列


def get_neighbors(
    vault: Vault,
    nid: str,
    rel_types: list[str] | None = None,
    direction: str = "both",
) -> list[RelationEdge]:
    """指定ノードの直接近傍を取得.

    Args:
        nid: ノード ID
        rel_types: フィルタするリレーション type（None なら全て）
        direction: "out" / "in" / "both"
    """
    edges: list[RelationEdge] = []

    if direction in ("out", "both"):
        for target, rtype, weight, evidence in vault.outgoing.get(nid, []):
            if rel_types and rtype not in rel_types:
                continue
            edges.append(
                RelationEdge(
                    source_nid=nid,
                    target_nid=target,
                    rel_type=rtype,
                    weight=weight,
                    evidence=evidence,
                    direction="out",
                )
            )

    if direction in ("in", "both"):
        for source, rtype, weight, evidence in vault.incoming.get(nid, []):
            if rel_types and rtype not in rel_types:
                continue
            edges.append(
                RelationEdge(
                    source_nid=source,
                    target_nid=nid,
                    rel_type=rtype,
                    weight=weight,
                    evidence=evidence,
                    direction="in",
                )
            )

    return edges


def bfs_traverse(
    vault: Vault,
    start_nid: str,
    max_depth: int = 2,
    rel_types: list[str] | None = None,
    direction: str = "both",
    target_layers: list[str] | None = None,
    min_weight: float = 0.0,
) -> list[TraversalNode]:
    """BFS で多段近傍を辿る.

    Args:
        start_nid: 起点ノード
        max_depth: 最大ホップ数
        rel_types: フィルタする relation type
        direction: "out" / "in" / "both"
        target_layers: 結果に含める層（None なら全て）
        min_weight: weight 下限フィルタ
    """
    start = vault.get(start_nid)
    if not start:
        return []

    visited: dict[str, TraversalNode] = {}
    queue: deque[tuple[str, int, list[RelationEdge]]] = deque()
    queue.append((start.nid, 0, []))
    visited[start.nid] = TraversalNode(note=start, depth=0, via=[])

    while queue:
        cur_nid, depth, path = queue.popleft()
        if depth >= max_depth:
            continue
        for edge in get_neighbors(vault, cur_nid, rel_types=rel_types, direction=direction):
            if edge.weight < min_weight:
                continue
            other = edge.target_nid if edge.direction == "out" else edge.source_nid
            if other in visited:
                continue
            other_note = vault.get(other)
            if not other_note:
                continue
            if target_layers and other_note.layer not in target_layers:
                # 経由は許すが結果に追加しない
                pass
            visited[other] = TraversalNode(
                note=other_note,
                depth=depth + 1,
                via=path + [edge],
            )
            queue.append((other, depth + 1, path + [edge]))

    results = list(visited.values())
    if target_layers:
        results = [r for r in results if r.note.layer in target_layers or r.depth == 0]
    results.sort(key=lambda r: (r.depth, -max((e.weight for e in r.via), default=0.0)))
    return results
