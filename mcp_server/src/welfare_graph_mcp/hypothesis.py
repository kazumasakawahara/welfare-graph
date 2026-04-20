"""支援仮説生成モジュール.

利用者プロファイル（または状況記述）から、4 レンズで支援仮説を生成。

4 レンズ:
  1. 法令適合: どの法令・ガイドライン下で支援すべきか
  2. サービス適格: どのサービスが利用可能/推奨されるか
  3. 技法マッチング: どの支援技法がエビデンス・整合性高く適応するか
  4. 類似事例: 似た特性で記録されているパターン
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .domain import find_applicable_laws, find_methods_for_disorder, find_services_for_profile
from .search import search_vault
from .vault import Note, Vault


@dataclass
class HypothesisLens:
    name: str
    findings: list[Note]
    notes: list[str] = field(default_factory=list)


@dataclass
class SupportHypothesis:
    profile_summary: str
    lenses: list[HypothesisLens]
    disclaimers: list[str]
    next_steps: list[str]


DISCLAIMERS = [
    "この仮説はあくまで候補です。最終判断は本人・家族・担当相談支援専門員等の合議で行ってください。",
    "個別ケースの法的・医学的判断は、担当の相談支援専門員・医師・弁護士等にご相談ください。",
    "情報は執筆時点のものです。最新情報は e-Gov・厚生労働省・自治体サイトで確認してください。",
    "本人の意思決定支援を最優先とし、支援者の都合で支援内容を決めないでください（意思決定支援ガイドライン参照）。",
]


def generate_hypothesis(
    vault: Vault,
    profile_text: str,
    disorders: list[str] | None = None,
    keywords: list[str] | None = None,
) -> SupportHypothesis:
    """4 レンズの支援仮説を生成.

    Args:
        profile_text: 利用者プロファイル・状況記述（自由テキスト）
        disorders: 既知の障害特性（明示指定があれば）
        keywords: 追加キーワード
    """
    lenses: list[HypothesisLens] = []

    # 自動推定: profile_text から障害特性らしきキーワードを抽出
    if not disorders:
        disorders = []
        common_disorders = [
            "知的障害", "自閉スペクトラム症", "注意欠如多動症", "ADHD", "ASD",
            "統合失調症", "うつ病", "双極性障害", "強度行動障害",
            "発達障害", "ダウン症", "パーソナリティ障害",
        ]
        for d in common_disorders:
            if d in profile_text:
                disorders.append(d)

    # Lens 1: 法令適合
    law_result = find_applicable_laws(vault, profile_text)
    lenses.append(HypothesisLens(
        name="法令適合（コンプライアンス）",
        findings=law_result.primary[:5],
        notes=law_result.rationale,
    ))

    # Lens 2: サービス適格
    svc_result = find_services_for_profile(
        vault,
        disorders=disorders,
        keywords=keywords,
    )
    lenses.append(HypothesisLens(
        name="サービス適格",
        findings=svc_result.primary[:8],
        notes=svc_result.rationale,
    ))

    # Lens 3: 技法マッチング
    method_findings: list[Note] = []
    method_notes: list[str] = []
    for d in disorders[:3]:
        m_result = find_methods_for_disorder(vault, d)
        method_notes.extend(m_result.rationale)
        for m in m_result.primary[:5]:
            if m not in method_findings:
                method_findings.append(m)
    lenses.append(HypothesisLens(
        name="技法マッチング（エビデンス）",
        findings=method_findings,
        notes=method_notes,
    ))

    # Lens 4: 類似事例（30_Insights から検索）
    insight_findings: list[Note] = []
    if profile_text:
        insight_hits = search_vault(vault, profile_text, layer="30_Insights", limit=5)
        insight_findings = [h.note for h in insight_hits]

    lenses.append(HypothesisLens(
        name="類似知見（30_Insights）",
        findings=insight_findings,
        notes=["過去の知見ノートから検索" if insight_findings else "類似知見なし"],
    ))

    # Next steps
    next_steps = [
        "✅ 本人・家族の意向を最優先で確認する（意思決定支援ガイドライン）",
        "✅ アセスメント結果（区分認定・行動関連項目等）を最新化する",
        "✅ 提示された法令の最新版を e-Gov で確認する",
        "✅ サービス事業所の空き状況・地域内提供状況を確認する",
        "✅ 担当者会議で本仮説をベースに議論する",
    ]
    if any(n.metadata.get("status") == "pending-amendment" for lens in lenses for n in lens.findings):
        next_steps.insert(0, "⚠ 改正予告中の法令/サービスが含まれる。最新動向を要確認")

    return SupportHypothesis(
        profile_summary=profile_text[:200],
        lenses=lenses,
        disclaimers=list(DISCLAIMERS),
        next_steps=next_steps,
    )
