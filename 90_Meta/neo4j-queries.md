<!-- allow-realname -->
---
type: meta
title: neo4j-queries
tags: [meta, neo4j, cypher]
cssclasses: [layer-meta]
updated: 2026-04-20
---

# Neo4j 実用クエリ集

welfare-graph を Neo4j に同期した後の、相談支援実務で使える Cypher クエリ集。Neo4j Browser（http://localhost:7474）に貼り付けて実行。

## 前提

- ノードラベル: `Node`（全ノード共通）
- 主要プロパティ: `nid`（パスベース ID）, `type`, `layer`, `title`, `cssclasses`, `status`, `version`, `effective_date`
- 関係タイプ: SCHEMA.md §4 参照（applies-to / has-characteristic / responds-to / 等）
- 関係プロパティ: `weight`, `evidence`, `rationale`, `condition`

---

## 1. 基本ナビゲーション

### 1.1 全ノード一覧（層別カウント）

```cypher
MATCH (n:Node)
RETURN n.layer AS layer, count(n) AS count
ORDER BY layer;
```

### 1.2 特定層の全ノード

```cypher
MATCH (n:Node {layer: '60_Laws'})
RETURN n.nid, n.title
ORDER BY n.title;
```

### 1.3 ノード詳細表示

```cypher
MATCH (n:Node {nid: '60_Laws/障害者総合支援法'})
RETURN n;
```

---

## 2. 利用者中心ビュー

### 2.1 P-0001 を中心とした近傍 2 ホップ

```cypher
MATCH path = (p:Node {nid: '10_People/P-0001'})-[*1..2]-(neighbor)
RETURN path
LIMIT 50;
```

### 2.2 P-0001 に関連する全法令

```cypher
MATCH (p:Node {nid: '10_People/P-0001'})-[r]->(law:Node {layer: '60_Laws'})
RETURN law.title, type(r), r.weight, r.evidence
ORDER BY r.weight DESC;
```

### 2.3 P-0001 が利用中のサービス

```cypher
MATCH (p:Node {nid: '10_People/P-0001'})-[r:`currently-using`]->(svc:Node {layer: '66_Services'})
RETURN svc.title, r.weight, r.evidence;
```

### 2.4 P-0001 に推奨される技法（weight 0.6 以上）

```cypher
MATCH (p:Node {nid: '10_People/P-0001'})-[r:recommended|`evidence-based`]->(m:Node {layer: '64_Methods'})
WHERE r.weight >= 0.6
RETURN m.title, type(r), r.weight, r.rationale
ORDER BY r.weight DESC;
```

---

## 3. 障害特性ベースの探索

### 3.1 自閉スペクトラム症に有効な技法

```cypher
MATCH (asd:Node {nid: '63_Disorders/自閉スペクトラム症'})-[r:`responds-to`]->(m:Node {layer: '64_Methods'})
RETURN m.title, r.weight, r.evidence
ORDER BY r.weight DESC;
```

### 3.2 自閉スペクトラム症に禁忌の技法

```cypher
MATCH (asd:Node {nid: '63_Disorders/自閉スペクトラム症'})-[r:contraindicated]->(m:Node {layer: '64_Methods'})
RETURN m.title, r.weight, r.rationale;
```

### 3.3 併存する障害

```cypher
MATCH (d1:Node {layer: '63_Disorders'})-[r:`comorbid-with`]-(d2:Node {layer: '63_Disorders'})
RETURN d1.title AS disorder, d2.title AS comorbid, r.weight
ORDER BY r.weight DESC;
```

---

## 4. 法令・サービス連携

### 4.1 ある法令を根拠とするサービス一覧

```cypher
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r:`mandated-by`|`law_basis`]-(svc:Node {layer: '66_Services'})
RETURN svc.title, type(r);
```

### 4.2 ある法令を根拠とする機関一覧

```cypher
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r:`mandated-by`]-(org:Node {layer: '67_Orgs'})
RETURN org.title, r.evidence;
```

### 4.3 サービスを提供する機関

```cypher
MATCH (svc:Node {nid: '66_Services/行動援護'})-[r:`provided-by`]->(org:Node {layer: '67_Orgs'})
RETURN org.title;
```

---

## 5. 改正追随分析（進化する知識グラフ）

### 5.1 ある法令の改正で影響を受けるノード

```cypher
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r]-(affected)
WHERE type(r) IN ['applies-to', 'mandated-by', 'compliance-required', 'law_basis']
RETURN affected.nid, affected.layer, type(r), r.weight
ORDER BY r.weight DESC;
```

### 5.2 高インパクト依存（weight ≥ 0.8）の利用者一覧

```cypher
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r]-(p:Node {layer: '10_People'})
WHERE r.weight >= 0.8
RETURN p.nid AS person, type(r), r.weight, r.evidence
ORDER BY r.weight DESC;
```

### 5.3 archived/ ノード一覧（旧版）

```cypher
MATCH (n:Node)
WHERE n.status = 'archived'
RETURN n.nid, n.version, n.effective_date_end
ORDER BY n.effective_date_end DESC;
```

### 5.4 版チェーン辿り（新版から旧版へ）

```cypher
MATCH path = (current:Node)-[:supersedes*]->(old:Node)
WHERE current.nid = '60_Laws/障害者総合支援法'
RETURN path;
```

### 5.5 pending-amendment 中のノード（要対応）

```cypher
MATCH (n:Node)
WHERE n.status = 'pending-amendment'
RETURN n.nid, n.version, n.review_due
ORDER BY n.review_due;
```

### 5.6 review_due 超過ノード

```cypher
MATCH (n:Node)
WHERE n.review_due IS NOT NULL AND date(n.review_due) < date()
RETURN n.nid, n.review_due, duration.between(date(n.review_due), date()).days AS days_overdue
ORDER BY days_overdue DESC;
```

---

## 6. 集計・俯瞰

### 6.1 ノード数（層 × type）

```cypher
MATCH (n:Node)
RETURN n.layer AS layer, n.type AS type, count(*) AS count
ORDER BY layer, type;
```

### 6.2 関係タイプ別集計

```cypher
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(*) AS count
ORDER BY count DESC;
```

### 6.3 高重み関係 Top 20

```cypher
MATCH (a:Node)-[r]->(b:Node)
WHERE r.weight IS NOT NULL AND r.weight >= 0.9
RETURN a.nid, type(r), b.nid, r.weight
ORDER BY r.weight DESC
LIMIT 20;
```

### 6.4 ノードの参照入次数 Top 10（よく参照される知識）

```cypher
MATCH (n:Node)<-[r]-()
RETURN n.nid, n.layer, count(r) AS in_degree
ORDER BY in_degree DESC
LIMIT 10;
```

### 6.5 孤児ノート（誰からも参照されていない）

```cypher
MATCH (n:Node)
WHERE NOT (n)<-[]-() AND NOT n.layer IN ['00_MOC', '90_Meta']
RETURN n.nid, n.layer
ORDER BY n.nid;
```

---

## 7. パス探索（複数ホップ）

### 7.1 利用者から法令への最短パス

```cypher
MATCH path = shortestPath(
  (p:Node {nid: '10_People/P-0001'})-[*..5]-(law:Node {nid: '60_Laws/障害者虐待防止法'})
)
RETURN path;
```

### 7.2 ある障害から到達可能なサービス（3 ホップ以内）

```cypher
MATCH path = (d:Node {nid: '63_Disorders/自閉スペクトラム症'})-[*1..3]-(svc:Node {layer: '66_Services'})
RETURN DISTINCT svc.title, length(path) AS hops
ORDER BY hops, svc.title;
```

### 7.3 共通の法令を持つ利用者ペア

```cypher
MATCH (p1:Node {layer: '10_People'})-[:`applies-to`|compliance-required]->(law:Node {layer: '60_Laws'})<-[:`applies-to`|compliance-required]-(p2:Node {layer: '10_People'})
WHERE p1.nid < p2.nid
RETURN p1.nid, p2.nid, law.title
ORDER BY law.title;
```

---

## 8. 横断分析（地域・複数利用者）

### 8.1 全利用者で利用率上位のサービス

```cypher
MATCH (p:Node {layer: '10_People'})-[r:`currently-using`]->(svc:Node {layer: '66_Services'})
RETURN svc.title, count(p) AS users
ORDER BY users DESC;
```

### 8.2 全利用者で参照頻度上位の障害特性

```cypher
MATCH (p:Node {layer: '10_People'})-[r:`has-characteristic`]->(d:Node {layer: '63_Disorders'})
RETURN d.title, count(p) AS users
ORDER BY users DESC;
```

### 8.3 推奨技法 vs 実適用のギャップ

```cypher
MATCH (p:Node {layer: '10_People'})-[r1:`has-characteristic`]->(d:Node)-[r2:`responds-to`]->(m:Node {layer: '64_Methods'})
WHERE NOT EXISTS {
  MATCH (p)-[:recommended|`evidence-based`]->(m)
}
RETURN p.nid, d.title, m.title AS suggested_method
ORDER BY p.nid;
```

「障害特性的には適応技法だが、利用者ノートには未記入」というギャップを抽出。支援計画見直しの起点になる。

---

## 9. 性教育・権利擁護横断

### 9.1 性教育・権利擁護関連ノードのネットワーク

```cypher
MATCH (n:Node)
WHERE n.title CONTAINS '性' OR n.title CONTAINS '権利' OR n.title CONTAINS '虐待'
   OR n.title CONTAINS 'CAP' OR n.title CONTAINS '意思決定'
RETURN n.nid, n.layer, n.title
ORDER BY n.layer;
```

### 9.2 虐待防止法から派生するノード

```cypher
MATCH (law:Node {nid: '60_Laws/障害者虐待防止法'})-[*1..2]-(neighbor)
RETURN DISTINCT neighbor.nid, neighbor.layer
ORDER BY neighbor.layer;
```

---

## 10. データ品質チェック

### 10.1 weight が 0-1 範囲外の関係

```cypher
MATCH ()-[r]->()
WHERE r.weight IS NOT NULL AND (r.weight < 0 OR r.weight > 1)
RETURN startNode(r).nid, type(r), endNode(r).nid, r.weight;
```

### 10.2 必須プロパティ欠損の検出（法令）

```cypher
MATCH (n:Node {layer: '60_Laws'})
WHERE n.source_url IS NULL OR n.version IS NULL OR n.effective_date IS NULL
RETURN n.nid, n.source_url, n.version, n.effective_date;
```

### 10.3 archived/ なのに superseded_by がない

```cypher
MATCH (n:Node)
WHERE n.status = 'archived' AND NOT (n)-[:`superseded-by`]->()
RETURN n.nid;
```

---

## 11. 可視化推奨パターン

### 11.1 P-0001 の支援エコシステム可視化

```cypher
MATCH (p:Node {nid: '10_People/P-0001'})-[r*1..2]-(neighbor)
WHERE neighbor.layer IN ['60_Laws', '63_Disorders', '64_Methods', '66_Services', '67_Orgs', '40_Stakeholders']
RETURN p, r, neighbor;
```

→ Neo4j Browser のグラフ表示で、P-0001 を中心とした支援関係図が見える

### 11.2 知識層全体のネットワーク

```cypher
MATCH (a:Node)-[r]->(b:Node)
WHERE a.layer IN ['60_Laws', '61_Guidelines', '62_Frameworks', '63_Disorders', '64_Methods', '65_Assessments', '66_Services', '67_Orgs']
  AND b.layer IN ['60_Laws', '61_Guidelines', '62_Frameworks', '63_Disorders', '64_Methods', '65_Assessments', '66_Services', '67_Orgs']
RETURN a, r, b
LIMIT 200;
```

---

## 12. 改正告知時の即応クエリパッケージ

法改正のニュースが出たとき、以下を順番に実行して影響を把握:

```cypher
// Step 1: 該当法令ノードを特定
MATCH (n:Node {layer: '60_Laws'})
WHERE n.title CONTAINS '総合支援'
RETURN n.nid, n.version, n.effective_date;

// Step 2: 影響波及範囲（ノード数）
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[]-(n)
RETURN n.layer, count(n) AS affected_count
ORDER BY affected_count DESC;

// Step 3: 高インパクト利用者のリスト
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[r]-(p:Node {layer: '10_People'})
WHERE r.weight >= 0.7
RETURN p.nid, type(r), r.weight;

// Step 4: 法令を根拠とするサービス（更新候補）
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[:`mandated-by`|`law_basis`]-(svc:Node {layer: '66_Services'})
RETURN svc.nid, svc.version, svc.review_due;

// Step 5: 派生・関連ガイドライン
MATCH (law:Node {nid: '60_Laws/障害者総合支援法'})<-[:`derived-from`|`mandated-by`]-(gl:Node {layer: '61_Guidelines'})
RETURN gl.nid, gl.version, gl.review_due;
```

---

## 13. インデックス推奨（パフォーマンス）

初期セットアップ時に実行:

```cypher
CREATE INDEX node_nid IF NOT EXISTS FOR (n:Node) ON (n.nid);
CREATE INDEX node_layer IF NOT EXISTS FOR (n:Node) ON (n.layer);
CREATE INDEX node_type IF NOT EXISTS FOR (n:Node) ON (n.type);
CREATE INDEX node_status IF NOT EXISTS FOR (n:Node) ON (n.status);
CREATE INDEX node_review_due IF NOT EXISTS FOR (n:Node) ON (n.review_due);
```

---

## 14. APOC 拡張クエリ（要 APOC プラグイン）

### 14.1 ノードの中心性算出

```cypher
CALL apoc.algo.degreeBetweenness('Node', 'IN', null)
YIELD node, score
RETURN node.nid, score
ORDER BY score DESC
LIMIT 10;
```

### 14.2 コミュニティ検出（Louvain）

```cypher
CALL gds.louvain.stream('myGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).nid AS node, communityId
ORDER BY communityId, node;
```

→ どのノードが「同じコミュニティ」に属するか自動分類。新たな知見の発見に有効。

---

## 関連

- [[neo4j-integration-design]] グラフ DB 設計書
- [[SCHEMA]] frontmatter / relations 仕様
- [[amendment-tracking]] 改正追随運用設計
- 同期スクリプト: `90_Meta/scripts/sync_to_neo4j.py`
