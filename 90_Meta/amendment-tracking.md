<!-- allow-realname -->
---
type: meta
title: amendment-tracking
tags: [meta, amendment, evolving-graph]
cssclasses: [layer-meta]
updated: 2026-04-20
---

# 改正追随運用設計（Evolving Knowledge Graph）

welfare-graph を「**一度作って終わり**」ではなく、**継続的に進化する知識グラフ** として運用するための設計書。LLM-Wiki の思想（版管理・差分統合・コミュニティ協働）を福祉領域に適用したもの。

## 1. 設計思想

### 1.1 なぜ必要か

- 障害福祉の法制度は **3 年ごとの報酬改定** で大きく変わる（次回 2027 年度）
- 法令（総合支援法・虐待防止法等）は不定期に改正される
- 厚労省ガイドラインは社会情勢・判例を反映して随時更新される
- 改定を反映できない知識グラフは、**時間とともに誤情報源に転落する**

### 1.2 LLM-Wiki 思想の福祉適用

| LLM-Wiki の原則 | welfare-graph での実装 |
|---|---|
| 版管理された知識ノード | `version`, `version_hash`, `amendment_history` frontmatter |
| 差分ベースの更新 | `law-amendment-integrate` スキルで diff 取込 |
| コミュニティ協働 | GitHub PR + `CONTRIBUTING.md` + コミット署名 |
| 時間軸での真偽評価 | `status: active/archived`, `effective_date`, `effective_date_end` |
| 自動鮮度検知 | `amendment_check.py` + `review_due` + RSS 監視 |
| ソースへの追跡可能性 | `source_url`, `source` フィールド, `raw/` 原本保管 |

## 2. 4 層アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│ Layer 4: 通知層                                      │
│   vault_health_check CRITICAL + GitHub Issue 自動起票 │
├─────────────────────────────────────────────────────┤
│ Layer 3: 統合層                                      │
│   law-amendment-integrate スキル → 差分取込・波及算出 │
├─────────────────────────────────────────────────────┤
│ Layer 2: 差分層                                      │
│   archived/ 退避 + supersedes チェーン + diff 記録     │
├─────────────────────────────────────────────────────┤
│ Layer 1: 検知層                                      │
│   amendment_check.py (review_due + version_hash 監視) │
└─────────────────────────────────────────────────────┘
```

### 2.1 Layer 1: 検知層

**目的**: 改正の兆しを早期検知する

**仕組み**:
1. **期限監視**: `review_due` フィールドが 30 日以内・超過の法令/ガイドライン/サービスを抽出
2. **ソースハッシュ比較**: `monitoring_url` を定期取得し、現在保存の `version_hash` と比較
3. **RSS / Atom 購読**: e-Gov 法令検索・厚労省新着情報の RSS を巡回
4. **キーワードウォッチ**: 「改正」「一部改正」「施行日」等のシグナルを検出

**実装**: `90_Meta/scripts/amendment_check.py`

**出力**: `90_Meta/amendment-reports/{YYYY-MM-DD}.md`

### 2.2 Layer 2: 差分層

**目的**: 旧版を失わず、新版との関係を明示する

**ワークフロー**:
```
改正検知 → raw/laws/{法令名}_{新版}.pdf 取得
         ↓
現行ノート {法令名}.md を archived/{法令名}_{旧版}.md に複製
         ↓
現行ノートを新版内容で更新
         ↓
archived 版に status: archived / superseded_by 付与
         ↓
新版に supersedes / amendment_history エントリ追加
```

**フォルダ構造**:
```
60_Laws/
├── 障害者総合支援法.md           # 現行（status: active）
└── archived/
    ├── 障害者総合支援法_H24.md    # 平成24年改正版
    └── 障害者総合支援法_R6.md     # 令和6年改正版
```

### 2.3 Layer 3: 統合層

**目的**: 差分を知識グラフ全体に反映する

**Claude スキル**: `law-amendment-integrate`

**処理ステップ**:
1. **差分読み取り**: `raw/laws/diff_YYYY.txt` または新旧 PDF を比較
2. **影響範囲算出**: Neo4j で当該法令を参照するノード一覧を取得
   ```cypher
   MATCH (law:Node {nid: $law_nid})<-[r]-(affected)
   WHERE r.type IN ['applies-to', 'mandated-by', 'compliance-required']
   RETURN affected.nid, r.type, r.weight
   ```
3. **relations 再評価**: 各影響ノードについて、改正後も relations が妥当か確認・weight 調整案を生成
4. **新規 relations 提案**: 新設サービス・新設義務に基づく relations を提案
5. **承認プロセス**: ユーザー確認後に一括反映

### 2.4 Layer 4: 通知層

**目的**: 相談支援専門員に改正を確実に伝える

**通知経路**:
1. `vault_health_check.py` の CRITICAL 項目として表示
2. GitHub Actions で月次ジョブ → Issue 自動起票
3. `00_MOC/Home.md` にバナー表示（改正予告中の法令一覧）

## 3. 運用プロトコル

### 3.1 平時（月次）

1. 毎月 1 日: `amendment_check.py` 実行（GitHub Actions 自動 or 手動）
2. レポート確認: `90_Meta/amendment-reports/{YYYY-MM-DD}.md`
3. 期限近接・改正告知ありのノートをレビュー

### 3.2 改正告知検知時

1. 一次情報確認（e-Gov・官報・厚労省サイト）
2. 当該ノートの `status` を `pending-amendment` に変更
3. `review_due` を告知に合わせて前倒し
4. `00_MOC/Home.md` にアラート追加

### 3.3 改正施行時

1. 原文 PDF を `raw/laws/` に配置
2. `law-amendment-integrate` スキル実行:
   ```
   Claude Code: raw/laws/障害者総合支援法_令和9年改正.pdf で
                60_Laws/障害者総合支援法.md を更新してください
   ```
3. 差分レビュー → 承認 → 新版として保存
4. 旧版は `archived/` に退避
5. 影響を受ける relations の再評価
6. `vault_health_check.py` で CRITICAL なし確認

### 3.4 定期見直し（3 年ごと報酬改定サイクル）

- 全 `66_Services/*.md` の `review_due` を改定施行日に設定
- 改定 6 か月前から準備開始
- 改定施行月に一斉更新

## 4. コミュニティ協働モデル

### 4.1 GitHub PR ベースの寄付

法改正情報に気づいた相談支援専門員が Pull Request で寄付する仕組み:

1. Fork → 該当ノート編集
2. PR テンプレートに従い記入（一次ソース URL 必須）
3. メンテナがレビュー（実名混入・一次ソース整合性チェック）
4. マージ → 全ユーザーが更新を享受

### 4.2 変更の真正性保証

- コミット署名（GPG/SSH）推奨
- Co-Authored-By で複数名の貢献を明記
- `source_url` と `last_verified` で根拠の追跡可能性を担保

## 5. エッジケースと対処

| ケース | 対処 |
|---|---|
| 改正告知はあるが施行日未定 | `status: pending-amendment` のまま `review_due` を半年先に |
| 新旧で制度設計が根本的に違う | 新版は別ファイル名で作成し `derived-from` 関係に |
| 経過措置期間中（旧版と新版が併存） | 両版とも `status: active` 可。`condition` フィールドで適用条件を明記 |
| 一次ソースが削除された | `archive.org` や Wayback Machine の URL を `source_url_backup` に |
| 相反する改正情報（通知と告示でずれ） | `contradicts` relation を張り、両方とも記録 |

## 6. 指標（KPI）

進化する知識グラフとしての健全性指標:

- **鮮度**: `review_due` 超過ノートの割合 < 5%
- **追随速度**: 改正施行から 30 日以内の反映率 > 80%
- **コミュニティ寄付**: 月次 PR 数 > 3 件（配布後の目標）
- **情報追跡性**: `source_url` 設定率 = 100%
- **版チェーン整合性**: archived/ に `superseded_by` 欠損なし

## 7. 将来拡張

### 7.1 短期（3 か月以内）

- [ ] `amendment_check.py` の e-Gov RSS 連携実装
- [ ] GitHub Actions ワークフロー（月次健全性チェック）
- [ ] `00_MOC/Home.md` の改正告知バナー自動生成

### 7.2 中期（半年以内）

- [ ] diff 可視化（旧版 ↔ 新版の mermaid タイムライン）
- [ ] 相談支援専門員コミュニティでの PR ワークフロー確立
- [ ] `law-amendment-integrate` の完全自動化（承認のみ人間）

### 7.3 長期（1 年以上）

- [ ] Neo4j に時系列次元を導入（`valid_from`, `valid_to` プロパティ）
- [ ] 版間差分の自動テキスト要約
- [ ] 他地域（介護保険・児童福祉）への横展開

## 8. 関連資料

- [[SCHEMA]] §7 改正追随フィールド仕様
- [[neo4j-integration-design]] グラフ DB 連携
- [[../README]] プロジェクト概要
- [[../docs/USER_GUIDE]] 利用者向け手順書（第13章・第14章）

---

**改正に追随できない知識グラフは、時間と共に誤情報源になる。追随できる仕組みを組み込んでこそ、5 年後も使い続けられる。**
