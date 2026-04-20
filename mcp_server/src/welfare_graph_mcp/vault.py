"""Vault loader and in-memory index.

welfare-graph vault の markdown ファイルを読み込み、frontmatter とリンクを解析して
検索・グラフ traversal で利用可能な構造化データに変換する。
"""

from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter


# プライバシー保護: 利用者個別ノートと暗号化ファイルは MCP 経由では公開しない
PRIVATE_DIRS = {
    "10_People",
    "20_Episodes",
    "30_Insights/hypotheses",
    "40_Stakeholders",
    "50_Resilience",
    "raw",
    ".obsidian",
    ".claude",
    ".github",
    "docs",
    "mcp_server",
    "90_Meta/health-reports",
    "90_Meta/amendment-reports",
    "90_Meta/scripts",
    "90_Meta/templates",
}

# ルート直下メタファイル等もMCP公開対象外
PRIVATE_FILES = {
    "90_Meta/alias_map.md",
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE-DOCS",
}


@dataclass
class Note:
    """単一の Markdown ノートを表現."""

    nid: str  # vault 相対パス（拡張子なし）= ノード ID
    path: Path  # 絶対パス
    rel_path: str  # vault 相対パス（拡張子あり）
    layer: str  # 第一階層（60_Laws 等）
    title: str
    metadata: dict[str, Any]
    content: str  # frontmatter を除いた本文
    relations: list[dict[str, Any]] = field(default_factory=list)
    archived: bool = False

    def __repr__(self) -> str:
        return f"Note({self.nid!r}, layer={self.layer!r})"


def _strip_leading_html_comments(content: str) -> str:
    """先頭の HTML コメント行を除去（realname-allow マーカー対応）."""
    lines = content.splitlines(keepends=True)
    while lines and (lines[0].strip().startswith("<!--") or lines[0].strip() == ""):
        lines.pop(0)
    return "".join(lines)


def _is_private(rel_path: str) -> bool:
    """プライバシー保護対象パスか判定."""
    if rel_path in PRIVATE_FILES:
        return True
    parts = Path(rel_path).parts
    for d in PRIVATE_DIRS:
        d_parts = d.split("/")
        if len(parts) >= len(d_parts) and list(parts[: len(d_parts)]) == d_parts:
            return True
    return False


def _extract_layer(rel_path: str) -> str:
    """vault 相対パスから第一階層を抽出."""
    parts = Path(rel_path).parts
    return parts[0] if parts else ""


def _is_archived(rel_path: str) -> bool:
    return "archived" in Path(rel_path).parts


class Vault:
    """vault 全体のインメモリ表現."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.notes: dict[str, Note] = {}  # nid -> Note
        self.notes_by_layer: dict[str, list[Note]] = defaultdict(list)
        self.notes_by_type: dict[str, list[Note]] = defaultdict(list)
        # 関係グラフ: nid -> [(target_nid, rel_type, weight, evidence), ...]
        self.outgoing: dict[str, list[tuple[str, str, float, str]]] = defaultdict(list)
        # 逆方向グラフ: target_nid -> [(source_nid, rel_type, weight, evidence), ...]
        self.incoming: dict[str, list[tuple[str, str, float, str]]] = defaultdict(list)
        self._loaded = False

    def load(self) -> None:
        """vault 全体を走査して Note を構築."""
        if self._loaded:
            return

        # Pass 1: ノート収集
        for md in self.root.rglob("*.md"):
            rel = md.relative_to(self.root)
            rel_str = str(rel)
            if _is_private(rel_str):
                continue

            try:
                raw = md.read_text(encoding="utf-8")
            except Exception:
                continue

            cleaned = _strip_leading_html_comments(raw)
            try:
                post = frontmatter.loads(cleaned)
            except Exception:
                continue

            meta = post.metadata or {}
            nid = str(rel.with_suffix(""))
            title = meta.get("title") or meta.get("law_name") or meta.get("guideline_name") \
                or meta.get("service_name") or meta.get("disorder_name") \
                or meta.get("method_name") or meta.get("framework_name") \
                or meta.get("assessment_name") or md.stem

            note = Note(
                nid=nid,
                path=md,
                rel_path=rel_str,
                layer=_extract_layer(rel_str),
                title=str(title),
                metadata=meta,
                content=post.content,
                relations=meta.get("relations") or [],
                archived=_is_archived(rel_str) or meta.get("status") == "archived",
            )
            self.notes[nid] = note
            self.notes_by_layer[note.layer].append(note)
            t = meta.get("type", "")
            if t:
                self.notes_by_type[t].append(note)

        # Pass 2: 関係グラフ構築
        for nid, note in self.notes.items():
            for rel in note.relations:
                if not isinstance(rel, dict):
                    continue
                target_link = rel.get("to", "")
                target = self._resolve_link(target_link)
                if not target:
                    continue
                rtype = rel.get("type", "related-to")
                weight = float(rel.get("weight", 0.5)) if rel.get("weight") else 0.5
                evidence = str(rel.get("evidence") or rel.get("rationale") or "")
                self.outgoing[nid].append((target, rtype, weight, evidence))
                self.incoming[target].append((nid, rtype, weight, evidence))

            # supersedes / superseded_by frontmatter からも関係生成
            for fm_key, rtype in [
                ("superseded_by", "superseded-by"),
                ("supersedes", "supersedes"),
            ]:
                fm_val = note.metadata.get(fm_key)
                if not fm_val:
                    continue
                target = self._resolve_link(str(fm_val))
                if not target:
                    continue
                self.outgoing[nid].append((target, rtype, 1.0, f"frontmatter.{fm_key}"))
                self.incoming[target].append((nid, rtype, 1.0, f"frontmatter.{fm_key}"))

        self._loaded = True

    def _resolve_link(self, wikilink: str) -> str | None:
        """wikilink ターゲットを nid に解決."""
        s = wikilink.strip()
        if s.startswith("[[") and s.endswith("]]"):
            s = s[2:-2]
        if "|" in s:
            s = s.split("|", 1)[0]
        s = s.strip()
        if not s:
            return None

        # 完全一致
        if s in self.notes:
            return s
        # suffix 一致（"障害者総合支援法" → "60_Laws/障害者総合支援法"）
        for nid in self.notes:
            if nid.endswith("/" + s) or nid == s:
                return nid
        # name 一致（最後のセグメントだけ）
        last = s.rsplit("/", 1)[-1]
        for nid in self.notes:
            if nid.rsplit("/", 1)[-1] == last:
                return nid
        return None

    def get(self, nid: str) -> Note | None:
        """ノートを取得（パス・短縮 ID どちらも受け付ける）."""
        if nid in self.notes:
            return self.notes[nid]
        resolved = self._resolve_link(nid)
        if resolved:
            return self.notes[resolved]
        return None

    def list_layer(self, layer: str) -> list[Note]:
        """指定層の全ノート."""
        return list(self.notes_by_layer.get(layer, []))

    def list_type(self, node_type: str) -> list[Note]:
        """指定 type の全ノート."""
        return list(self.notes_by_type.get(node_type, []))

    def stats(self) -> dict[str, Any]:
        """vault 統計."""
        return {
            "total_notes": len(self.notes),
            "by_layer": {layer: len(notes) for layer, notes in self.notes_by_layer.items()},
            "by_type": {t: len(notes) for t, notes in self.notes_by_type.items()},
            "total_relations": sum(len(rels) for rels in self.outgoing.values()),
            "vault_root": str(self.root),
        }


def load_vault_from_env() -> Vault:
    """環境変数 WELFARE_GRAPH_VAULT から vault を読込."""
    vault_path = os.environ.get("WELFARE_GRAPH_VAULT")
    if not vault_path:
        # フォールバック: パッケージインストール元から推定
        # (このパッケージが welfare-graph/mcp_server/ 配下にある想定)
        here = Path(__file__).resolve()
        for parent in here.parents:
            if (parent / "00_MOC").exists() and (parent / "60_Laws").exists():
                vault_path = str(parent)
                break

    if not vault_path:
        raise RuntimeError(
            "WELFARE_GRAPH_VAULT 環境変数を設定してください。"
            "例: export WELFARE_GRAPH_VAULT=/path/to/welfare-graph"
        )

    root = Path(vault_path)
    if not root.exists():
        raise RuntimeError(f"vault パスが存在しません: {root}")

    vault = Vault(root)
    vault.load()
    return vault
