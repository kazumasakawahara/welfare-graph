<!-- allow-realname -->
---
type: meta
title: "Neo4j 連携設計書"
tags: [meta, neo4j, integration, design]
cssclasses: [layer-meta]
created: 2026-04-20
updated: 2026-04-20
---

# Neo4j 連携設計書

Obsidian vault の `relations` を **Neo4j グラフDB** に同期し、高度なクエリ（パス探索・中心性・クラスタリング）を可能にする設計書。

## 目的

Obsidian の `[[wikilink]]` と frontmatter `relations` は、人が読むのには最適だが、**以下の計算は困難**:

- 「P-0001 から 3 ホップ以内で到達可能な全サービス」
- 「全ケースで最も参照される技法 Top 10」
- 「法令→ガイドライン→サービス→技法 の標準パスが存在しないペア」
- 「利用者間のプロファイル類似度」
- 「孤立したサブグラフ（どの P-XXXX にもリンクしない法令）」

Neo4j に同期すれば、これらを Cypher で瞬時に解ける。

## アーキテクチャ

```
┌──────────────────────────┐      同期       ┌─────────────────────┐
│ Obsidian Vault           │  ───────────→  │ Neo4j Graph DB      │
│ (my-skill-graph)         │                 │                     │
│                          │                 │ Nodes:              │
│ - frontmatter            │                 │   Law / Guideline   │
│ - relations 配列         │                 │   Framework /       │
│ - [[wikilink]]           │                 │   Disorder / Method │
│                          │                 │   Service / Org /   │
│ * 人が読むメディア        │                 │   Person / Insight  │
│ * 編集の中心              │                 │                     │
│                          │                 │ Relationships:      │
│                          │                 │   APPLIES_TO /      │
│                          │                 │   COMPLIANCE_REQ /  │
│                          │  ←───── 可視化 ──│   RECOMMENDED / ... │
│                          │    （Neo4j      │                     │
│                          │     Browser or  │ * 機械が辿るメディア │
│                          │     Sigma.js）  │ * クエリ中心        │
└──────────────────────────┘                 └─────────────────────┘
     ↑編集                                        ↑クエリ
     Claude + 人                                  Claude + 可視化ツール
```

## ノードスキーマ

### 共通プロパティ
- `id`: ノート識別子（例: `P-0001`, `60_Laws/障害者総合支援法`）
- `type`: `Law` / `Guideline` / `Framework` / `Disorder` / `Method` / `Assessment` / `Service` / `Org` / `Person` / `Insight`
- `name`: 表示名
- `path`: Obsidian 上のファイルパス
- `updated`: 最終更新日
- `tags`: 配列

### ノード種別（ラベル）

#### Law（法令）
```cypher
(:Law {
  id: "60_Laws/障害者総合支援法",
  name: "障害者総合支援法",
  source_url: "...",
  version: "令和6年改正",
  effective_date: date("2024-04-01"),
  review_due: date("2027-04-01"),
  issuer: "厚生労働省"
})
```

#### Service（サービス）
```cypher
(:Service {
  id: "66_Services/行動援護",
  name: "行動援護",
  law_basis: "障害者総合支援法",
  target: "区分3以上+行動関連10点以上",
  fee_code: "115",
  version: "令和6年度報酬改定"
})
```

#### Disorder / Method / Framework 等も同様。

#### Person（利用者）
```cypher
(:Person {
  id: "P-0001",
  name: "P-0001",
  diagnosis: ["知的障害", "自閉スペクトラム症"],
  disability_cert: "療育手帳B",
  status: "active"
})
```

## リレーションシップスキーマ

frontmatter `relations.type` を Neo4j 関係タイプに変換:

| Obsidian type | Neo4j relationship | プロパティ |
|---|---|---|
| `applies-to` | `APPLIES_TO` | weight, evidence |
| `compliance-required` | `COMPLIANCE_REQUIRED` | weight, condition |
| `mandatory-report-trigger` | `MANDATORY_REPORT_TRIGGER` | weight |
| `eligible-service` | `ELIGIBLE_FOR` | weight, rationale |
| `currently-using` | `USING` | weight, source |
| `considered` | `CONSIDERED` | weight |
| `discontinued` | `DISCONTINUED` | weight, since |
| `has-characteristic` | `HAS_CHARACTERISTIC` | weight |
| `responds-to` | `RESPONDS_TO` | weight |
| `contraindicated` | `CONTRAINDICATED` | weight |
| `recommended` | `RECOMMENDED` | weight |
| `evidence-based` | `EVIDENCE_BASED` | weight |
| `underpinned-by` | `UNDERPINNED_BY` | weight |
| `comorbid-with` | `COMORBID_WITH` | weight |
| `provided-by` | `PROVIDED_BY` | weight |
| `mandated-by` | `MANDATED_BY` | weight |
| `escalate-to` | `ESCALATE_TO` | weight, condition |
| `complements` | `COMPLEMENTS` | weight |
| `contradicts` | `CONTRADICTS` | weight |
| `supersedes` | `SUPERSEDES` | weight |

## 同期フロー

### オプションA: フル再ビルド（単純・確実）

1. 全 `.md` の frontmatter を解析
2. Neo4j をクリア
3. 全ノード作成
4. 全関係作成

毎回実行可能。小規模 vault（〜1000ノード）なら数秒。

### オプションB: 差分同期（効率的）

1. Obsidian 側で変更検知（git diff or 最終更新時刻）
2. 変更ファイルのみノード更新
3. 関係は対象ファイル分のみ削除・再作成

変更量が少ない場合に効率的。

### 実装技術

#### Python による同期スクリプト例

```python
import frontmatter
import glob
from neo4j import GraphDatabase
from pathlib import Path

VAULT_PATH = Path("/Users/k-kawahara/Obsidian/my-skill-graph")
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")

def sync_vault():
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

    with driver.session() as session:
        # 1. 既存データクリア
        session.run("MATCH (n) DETACH DELETE n")

        # 2. ノード作成
        for md_path in VAULT_PATH.glob("**/*.md"):
            if ".obsidian" in str(md_path) or "raw/" in str(md_path):
                continue
            with open(md_path) as f:
                post = frontmatter.load(f)
            if not post.metadata:
                continue
            create_node(session, md_path, post.metadata)

        # 3. 関係作成
        for md_path in VAULT_PATH.glob("**/*.md"):
            with open(md_path) as f:
                post = frontmatter.load(f)
            if "relations" not in post.metadata:
                continue
            for rel in post.metadata["relations"]:
                create_relationship(session, md_path, rel)

    driver.close()

def create_node(session, path, meta):
    node_type = meta.get("type", "Unknown")
    label = capitalize(node_type)
    props = {k: v for k, v in meta.items() if v is not None}
    props["path"] = str(path.relative_to(VAULT_PATH))
    session.run(
        f"CREATE (n:{label} $props)",
        props=props
    )

def create_relationship(session, source_path, rel):
    rel_type = rel["type"].upper().replace("-", "_")
    to_wikilink = rel["to"]  # "[[...]]" 形式
    target_id = extract_id(to_wikilink)
    session.run(
        f"""
        MATCH (a {{path: $source_path}}), (b {{path: $target_id}})
        CREATE (a)-[r:{rel_type} $props]->(b)
        """,
        source_path=str(source_path.relative_to(VAULT_PATH)),
        target_id=target_id,
        props={
            "weight": rel.get("weight", 0.5),
            "evidence": rel.get("evidence", ""),
            "rationale": rel.get("rationale", ""),
            "condition": rel.get("condition", "")
        }
    )

if __name__ == "__main__":
    sync_vault()
```

#### 依存関係

```bash
pip install neo4j python-frontmatter
```

#### Neo4j 本体

- Docker: `docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j`
- Neo4j Desktop (ローカル)
- Neo4j Aura (クラウド、無料枠あり)

## 代表的な Cypher クエリ

### 1. P-0001 から 3 ホップで到達可能な全サービス

```cypher
MATCH path = (p:Person {id: "P-0001"})-[*1..3]-(s:Service)
RETURN DISTINCT s.name, length(path) AS hops
ORDER BY hops
```

### 2. 全利用者に共通して推奨される技法 Top 10

```cypher
MATCH (p:Person)-[r:RECOMMENDED|EVIDENCE_BASED]->(m:Method)
RETURN m.name AS method, count(p) AS num_persons, avg(r.weight) AS avg_weight
ORDER BY num_persons DESC, avg_weight DESC
LIMIT 10
```

### 3. 最も参照される法令（中心性）

```cypher
MATCH (l:Law)<-[r]-()
RETURN l.name, count(r) AS referenced_count
ORDER BY referenced_count DESC
```

### 4. P-0001 と類似プロフィールの利用者検索

```cypher
MATCH (p1:Person {id: "P-0001"})-[:HAS_CHARACTERISTIC]->(d:Disorder)<-[:HAS_CHARACTERISTIC]-(p2:Person)
WHERE p1 <> p2
RETURN p2.id, collect(d.name) AS shared_disorders, count(d) AS similarity
ORDER BY similarity DESC
```

### 5. 法令→サービス の未接続パス（適格可能性の漏れ）

```cypher
MATCH (p:Person)-[:HAS_CHARACTERISTIC]->(d:Disorder)
MATCH (s:Service)-[:APPLIES_TO]->(d)
WHERE NOT EXISTS((p)-[:USING|ELIGIBLE_FOR|CONSIDERED]->(s))
RETURN p.id, d.name, s.name
```

### 6. 特定技法（構造化支援）から辿れる利用者

```cypher
MATCH (m:Method {name: "構造化支援"})<-[:RECOMMENDED|EVIDENCE_BASED]-(p:Person)
RETURN p.id, p.diagnosis
```

### 7. 法令→ガイドライン→技法 の標準パス

```cypher
MATCH path = (l:Law)-[:COMPLEMENTS|APPLIES_TO]->(g:Guideline)-[:COMPLEMENTS]->(m:Method)
RETURN l.name, g.name, m.name
```

## 可視化

### Neo4j Browser
- Cypher を打ちながら探索
- ノードをクリックで属性表示
- グラフを直接操作

### Sigma.js 等のカスタム可視化

既存の `neo4j-graph-viz` スキル（ヘッドCLAUDE.mdに記載）を活用:
- HTML + Sigma.js でインタラクティブな知識グラフ生成
- 単一スクリプトで完結
- ブラウザで閲覧可

## 同期タイミング

- **手動**: コミット前、重要な更新後
- **自動**: cron / GitHub Actions で毎日深夜
- **イベントドリブン**: Obsidian の file watcher（プラグイン経由）

## セキュリティ

### 個人情報保護

- Neo4j インスタンスは **ローカル限定**（公開クラウドは避ける）
- パスワード・認証の厳格化
- バックアップの暗号化

### 実名混入防止

- 同期時に `alias_map.md` は読まない
- `<!-- allow-realname -->` の有無にかかわらず仮名IDのみ処理
- 同期ログに実名を残さない

## 運用

### 初回セットアップ

1. Neo4j 起動（Docker / Desktop）
2. Python 環境準備
3. 同期スクリプト実行
4. Neo4j Browser でクエリ試行

### 日常運用

1. Obsidian で編集
2. 定期的に（or コミット時）同期スクリプト実行
3. Neo4j で分析クエリ
4. 結果を Obsidian 運用に還元

### データ整合性

- Obsidian が **正** （Source of Truth）
- Neo4j は **派生** データ
- 不整合時は Neo4j を再構築

## 将来拡張

### 1. LLM との統合
- Claude が Cypher を書いて Neo4j に問い合わせ → 結果を自然言語で回答
- MCP の neo4j サーバー経由

### 2. 時系列データ
- モニタリング履歴を時系列ノードとして追加
- 変化のパターン検出

### 3. 機械学習
- Person の類似度計算（Graph Embeddings）
- 支援成功パターンの予測

### 4. 他 vault との統合
- 他の相談支援事業所の匿名化データとの合流
- 地域全体の傾向分析

## 関連スキル・ツール

- `neo4j-graph-viz`: Sigma.js 可視化
- `neo4j-cypher-guide`: Cypher クエリガイド
- `neo4j-support-db`: 類似目的の別vault用スキル
- `support-hypothesis`: Obsidian側の relations 活用

## 実装優先順位

1. **Phase 1（最低限）**: Python スクリプトでフル同期、Neo4j Browser で探索
2. **Phase 2**: 差分同期、クエリライブラリ（よく使うクエリのテンプレ）
3. **Phase 3**: Sigma.js 可視化、Obsidian側への結果フィードバック
4. **Phase 4**: LLM統合、自動分析

## 実装しない場合の代替

Neo4j を導入しない場合でも、以下で部分的な機能を実現可能:

- **Dataview プラグイン**: Obsidian内でクエリ実行（範囲は限定的）
- **Python スクリプト**: frontmatter を読んで集計（グラフ走査は自前実装）
- **`neo4j-graph-viz` スキル**: 任意のサブグラフを HTML化（Neo4j 必須だが可視化は軽量）

## 参考資料

- Neo4j公式: https://neo4j.com/docs/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/
- python-frontmatter: https://python-frontmatter.readthedocs.io/
- 既存の `neo4j-support-db` スキル（類似vault向け）
