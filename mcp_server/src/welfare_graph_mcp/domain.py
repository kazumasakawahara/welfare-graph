"""ドメイン特化ロジック.

障害福祉特有の問い合わせ（状況→法令、障害→技法、属性→サービス）を実装。
"""

from __future__ import annotations

from dataclasses import dataclass

from .search import _tokenize_query, search_vault
from .traverse import bfs_traverse, get_neighbors
from .vault import Note, Vault


# 状況キーワード → 関連法令名のマッピング（簡易ヒューリスティック）
SITUATION_KEYWORDS = {
    "虐待": ["障害者虐待防止法", "障害者虐待防止マニュアル", "身体拘束適正化の手引"],
    "通報": ["障害者虐待防止法"],
    "差別": ["障害者差別解消法"],
    "合理的配慮": ["障害者差別解消法"],
    "成年後見": ["成年後見制度", "意思決定支援を踏まえた後見事務のガイドライン"],
    "意思決定": ["意思決定支援ガイドライン"],
    "サービス利用": ["障害者総合支援法", "サービス等利用計画作成サポートブック"],
    "就労": ["障害者総合支援法", "就労選択支援_運営要綱"],
    "性的虐待": ["障害者虐待防止法", "障害者施設における性的虐待の防止と対応"],
    "性教育": ["障害者施設における性的虐待の防止と対応"],
    "強度行動障害": ["強度行動障害支援者養成研修テキスト"],
    "地域移行": ["地域移行支援の手引"],
    "モニタリング": ["モニタリング標準期間通知"],
    "身体拘束": ["身体拘束適正化の手引"],
    "精神保健": ["精神保健福祉法"],
    "発達障害": ["発達障害者支援法"],
    "刑事": ["刑法性犯罪規定"],
    "性犯罪": ["刑法性犯罪規定"],
    "母体保護": ["母体保護法"],
    "優生保護": ["旧優生保護法"],
}


@dataclass
class DomainResult:
    """ドメイン特化問い合わせの結果."""

    primary: list[Note]  # 主要該当
    related: list[Note]  # 関連
    rationale: list[str]  # 推論プロセスの説明


def find_applicable_laws(vault: Vault, situation: str) -> DomainResult:
    """状況記述から該当する可能性が高い法令を抽出.

    シンプルなキーワードマッチ + 関係グラフ探索の併用。
    """
    rationale: list[str] = []
    matched_law_names: set[str] = set()

    # キーワードマッチ
    situation_lower = situation.lower()
    for keyword, laws in SITUATION_KEYWORDS.items():
        if keyword in situation_lower or keyword in situation:
            matched_law_names.update(laws)
            rationale.append(f"キーワード『{keyword}』→ {', '.join(laws)}")

    # 法令ノートに変換
    primary: list[Note] = []
    seen: set[str] = set()
    for name in matched_law_names:
        for layer in ("60_Laws", "61_Guidelines"):
            note = vault.get(f"{layer}/{name}")
            if note and note.nid not in seen:
                primary.append(note)
                seen.add(note.nid)

    # キーワードマッチがない場合は法令層を全文検索
    if not primary:
        rationale.append("キーワード辞書ヒットなし → 全文検索")
        for layer in ("60_Laws", "61_Guidelines"):
            hits = search_vault(vault, situation, layer=layer, limit=5)
            for hit in hits:
                if hit.note.nid not in seen:
                    primary.append(hit.note)
                    seen.add(hit.note.nid)

    # 関連ノートを relations から取得
    related: list[Note] = []
    for note in primary[:3]:
        for edge in get_neighbors(vault, note.nid, direction="out"):
            other = vault.get(edge.target_nid)
            if other and other.layer in ("60_Laws", "61_Guidelines") and other.nid not in seen:
                related.append(other)
                seen.add(other.nid)

    return DomainResult(primary=primary, related=related[:10], rationale=rationale)


def find_methods_for_disorder(vault: Vault, disorder_name: str) -> DomainResult:
    """障害特性 → 適応する支援技法（responds-to + recommended + evidence-based）."""
    rationale: list[str] = []

    # 障害ノート特定
    disorder_note = vault.get(f"63_Disorders/{disorder_name}") or vault.get(disorder_name)
    if not disorder_note:
        # 検索フォールバック
        hits = search_vault(vault, disorder_name, layer="63_Disorders", limit=3)
        if hits:
            disorder_note = hits[0].note
            rationale.append(f"検索により '{disorder_note.title}' を特定")
        else:
            return DomainResult(primary=[], related=[], rationale=[f"障害特性『{disorder_name}』が見つかりません"])

    rationale.append(f"対象障害: {disorder_note.title}")

    # 適応技法（responds-to）
    primary: list[Note] = []
    contraindicated: list[Note] = []

    for edge in get_neighbors(vault, disorder_note.nid, direction="out"):
        target = vault.get(edge.target_nid)
        if not target or target.layer != "64_Methods":
            continue
        if edge.rel_type == "responds-to":
            if target not in primary:
                primary.append(target)
        elif edge.rel_type == "contraindicated":
            contraindicated.append(target)

    # weight でソート
    primary.sort(key=lambda n: -max(
        (w for _, rt, w, _ in vault.outgoing.get(disorder_note.nid, [])
         if rt == "responds-to" and _ == n.nid),
        default=0.0,
    ))

    if primary:
        rationale.append(f"responds-to 関係: {len(primary)} 件")
    if contraindicated:
        rationale.append(f"⚠ 禁忌技法: {', '.join(n.title for n in contraindicated)}")

    # 関連: 併存障害
    related: list[Note] = list(contraindicated)
    for edge in get_neighbors(vault, disorder_note.nid, rel_types=["comorbid-with"], direction="both"):
        other = edge.target_nid if edge.direction == "out" else edge.source_nid
        if other == disorder_note.nid:
            continue
        n = vault.get(other)
        if n and n not in related:
            related.append(n)

    return DomainResult(primary=primary, related=related, rationale=rationale)


def find_services_for_profile(
    vault: Vault,
    disorders: list[str] | None = None,
    keywords: list[str] | None = None,
    eligibility_hints: dict | None = None,
) -> DomainResult:
    """障害特性・属性からサービスを探索.

    Args:
        disorders: 障害特性の名前リスト（例: ["自閉スペクトラム症", "知的障害"]）
        keywords: 自由キーワード（例: ["就労", "通所"]）
        eligibility_hints: 区分・年齢等のヒント
    """
    rationale: list[str] = []
    primary_set: dict[str, Note] = {}  # nid -> Note （重複排除）

    # 1. 障害特性経由でサービスを辿る
    if disorders:
        for d_name in disorders:
            d_note = vault.get(f"63_Disorders/{d_name}") or vault.get(d_name)
            if not d_note:
                continue
            rationale.append(f"障害『{d_note.title}』から関連サービスを探索")
            # 障害から 2 ホップ以内のサービス
            traversal = bfs_traverse(
                vault,
                d_note.nid,
                max_depth=3,
                target_layers=["66_Services"],
                min_weight=0.4,
            )
            for tn in traversal:
                if tn.note.layer == "66_Services" and tn.note.nid not in primary_set:
                    primary_set[tn.note.nid] = tn.note

    # 2. キーワードでサービス層を直接検索
    if keywords:
        query = " ".join(keywords)
        rationale.append(f"キーワード検索: {query}")
        for hit in search_vault(vault, query, layer="66_Services", limit=15):
            if hit.note.nid not in primary_set:
                primary_set[hit.note.nid] = hit.note

    primary = list(primary_set.values())

    # 関連: 提供機関
    related: list[Note] = []
    for svc in primary[:5]:
        for edge in get_neighbors(vault, svc.nid, rel_types=["provided-by"], direction="out"):
            org = vault.get(edge.target_nid)
            if org and org not in related:
                related.append(org)

    return DomainResult(primary=primary, related=related[:10], rationale=rationale)


def check_amendment_status(vault: Vault, domain: str | None = None) -> dict:
    """改正追随状況のサマリ.

    Args:
        domain: "60_Laws" / "61_Guidelines" / "66_Services" / None（全て）
    """
    from datetime import date, datetime

    today = date.today()

    layers = [domain] if domain else ["60_Laws", "61_Guidelines", "66_Services"]

    pending: list[tuple[Note, str]] = []
    expired: list[tuple[Note, int]] = []
    due_soon: list[tuple[Note, int]] = []
    archived_count = 0
    total = 0

    for layer in layers:
        for note in vault.list_layer(layer):
            if note.archived:
                archived_count += 1
                continue
            total += 1
            status = note.metadata.get("status", "active")
            if status == "pending-amendment":
                pending.append((note, str(note.metadata.get("review_due", "未設定"))))

            rd = note.metadata.get("review_due")
            if isinstance(rd, str):
                try:
                    rd = datetime.strptime(rd, "%Y-%m-%d").date()
                except ValueError:
                    rd = None
            elif isinstance(rd, datetime):
                rd = rd.date()
            if isinstance(rd, date):
                delta = (rd - today).days
                if delta < 0:
                    expired.append((note, -delta))
                elif delta <= 90:
                    due_soon.append((note, delta))

    return {
        "domain": domain or "all",
        "total_active": total,
        "archived": archived_count,
        "pending_amendment": [
            {"nid": n.nid, "title": n.title, "review_due": d} for n, d in pending
        ],
        "expired": [
            {"nid": n.nid, "title": n.title, "days_overdue": d} for n, d in expired
        ],
        "due_soon": [
            {"nid": n.nid, "title": n.title, "days_remaining": d} for n, d in due_soon
        ],
        "checked_at": today.isoformat(),
    }
