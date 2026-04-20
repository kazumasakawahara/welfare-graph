<!-- allow-realname -->
---
type: meta
title: "彩色セットアップ手順"
tags: [meta, setup, colors]
cssclasses: [layer-meta]
updated: 2026-04-20
---

# 彩色システム セットアップ手順

色が反映されない場合、以下を順に実施してください。

## 🔧 手順（必須・順序厳守）

### 1. Obsidian をいったん完全に閉じる

**重要**: Obsidian が開いている間、`.obsidian/` 内の JSON ファイルは Obsidian が自分の設定で上書きします。起動中に graph.json を編集しても無効化されます。

- Mac: `Cmd+Q` で完全終了（ウィンドウを閉じるだけでは不十分）
- Windows: タスクバーからも終了確認

### 2. 設定ファイルの確認

Obsidian 終了中に以下が正しい内容になっているか確認:

```bash
cat .obsidian/graph.json | head -20
```

`colorGroups` に14個のエントリがあればOK。空配列 `[]` になっている場合、本リポジトリの状態で再上書きしてください（このドキュメント末尾の復元コマンド）。

### 3. Obsidian 再起動

- vault を開く
- 数秒待機（初期化）

### 4. CSS snippet の有効化

1. **設定** (`Cmd+,`) を開く
2. **外観**（Appearance）を選択
3. 下部の **CSS snippets** セクションまでスクロール
4. 🔄 リフレッシュボタンをクリック（`.obsidian/snippets/` を再読込）
5. `layer-colors` のトグルを **ON** にする

### 5. 動作確認

#### ファイルエクスプローラー
- 左サイドバーのフォルダ名が色付けされる
  - `60_Laws` → 赤
  - `64_Methods` → 緑
  - `66_Services` → 青
  - ...

#### グラフビュー
1. 左サイドバーの **グラフビューを開く**（`Cmd+G` または アイコン）
2. 左パネルの **フィルター** アイコン
3. **カラーグループ**（Color groups）を展開
4. 14個のパスベース色グループが表示されれば成功
5. グラフ上でノードが層ごとに色分けされる

### 6. タイトル彩色の有効化（個別ページ）

各ページの frontmatter に `cssclasses` を追加するとタイトル左に色アクセントが付きます:

```yaml
---
type: law
cssclasses: [layer-law]
tags: [law]
---
```

対応値は [[SCHEMA]] 参照。既存ページへの一括追加は別途作業。

---

## ❌ トラブルシューティング

### グラフビューで色が出ない

1. **Obsidian を完全終了してから再起動** しましたか？
2. `.obsidian/graph.json` の `colorGroups` が空配列 `[]` になっていないか確認
3. 下記の復元コマンドで再書き込み

### ファイルエクスプローラーで色が出ない

1. 設定 → 外観 → CSS snippets → `layer-colors` が **ON** か確認
2. リフレッシュボタン 🔄 を押す
3. Obsidian を再起動

### 一部のフォルダだけ色が付かない

- フォルダ名が `60_Laws` / `60_laws` / `60Laws` のどれか確認（大文字小文字・アンダースコア必須）
- CSS snippet のセレクタは `data-path^="60_Laws"` なので、パスの先頭文字が完全一致必要

### タイトル色が出ない

- 個別ページに `cssclasses: [layer-law]` 等が frontmatter に入っているか確認
- スペース・カンマ区切りの形式ミスに注意: `cssclasses: [layer-law]`（角括弧・カンマ）

---

## 📋 復元コマンド

`.obsidian/graph.json` が空に戻ってしまった場合の復元（Obsidian を必ず閉じてから実行）:

```bash
cd /Users/k-kawahara/Obsidian/my-skill-graph
cat > .obsidian/graph.json <<'EOF'
{
  "collapse-filter": true,
  "search": "",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": false,
  "showOrphans": true,
  "collapse-color-groups": false,
  "colorGroups": [
    { "query": "path:00_MOC/",         "color": { "a": 1, "rgb": 16752640 } },
    { "query": "path:10_People/",      "color": { "a": 1, "rgb": 4545124 } },
    { "query": "path:20_Episodes/",    "color": { "a": 1, "rgb": 6381921 } },
    { "query": "path:30_Insights/",    "color": { "a": 1, "rgb": 8550167 } },
    { "query": "path:40_Stakeholders/", "color": { "a": 1, "rgb": 24676 } },
    { "query": "path:50_Resilience/",  "color": { "a": 1, "rgb": 11342935 } },
    { "query": "path:60_Laws/",        "color": { "a": 1, "rgb": 12986408 } },
    { "query": "path:61_Guidelines/",  "color": { "a": 1, "rgb": 15690752 } },
    { "query": "path:62_Frameworks/",  "color": { "a": 1, "rgb": 6953882 } },
    { "query": "path:63_Disorders/",   "color": { "a": 1, "rgb": 16361509 } },
    { "query": "path:64_Methods/",     "color": { "a": 1, "rgb": 3046706 } },
    { "query": "path:65_Assessments/", "color": { "a": 1, "rgb": 6111287 } },
    { "query": "path:66_Services/",    "color": { "a": 1, "rgb": 1402304 } },
    { "query": "path:67_Orgs/",        "color": { "a": 1, "rgb": 33679 } }
  ],
  "collapse-display": true,
  "showArrow": true,
  "textFadeMultiplier": 0,
  "nodeSizeMultiplier": 1.2,
  "lineSizeMultiplier": 1,
  "collapse-forces": true,
  "centerStrength": 0.518713248970312,
  "repelStrength": 10,
  "linkStrength": 1,
  "linkDistance": 250,
  "scale": 0.9,
  "close": true
}
EOF
```

---

## 🎨 代替方法: UI からの手動設定（graph.json が上書きされ続ける場合）

graph.json 方式がうまくいかない場合、Obsidian UI から手動で設定できます:

1. グラフビューを開く（`Cmd+G`）
2. 左の **フィルター** パネル
3. **カラーグループ** → **＋ 新しいグループ**
4. 検索クエリ: `path:60_Laws/`
5. 色を選択（下記色票参照）
6. 14層分繰り返し

### 色票（UI用）

| 層 | HEX | 色名 |
|---|---|---|
| 00_MOC | `#FFA000` | Gold |
| 10_People | `#455A64` | Blue-Gray |
| 20_Episodes | `#616161` | Gray |
| 30_Insights | `#827717` | Olive |
| 40_Stakeholders | `#006064` | Dark Cyan |
| 50_Resilience | `#AD1457` | Pink |
| 60_Laws | `#C62828` | Red |
| 61_Guidelines | `#EF6C00` | Orange |
| 62_Frameworks | `#6A1B9A` | Purple |
| 63_Disorders | `#F9A825` | Amber |
| 64_Methods | `#2E7D32` | Green |
| 65_Assessments | `#5D4037` | Brown |
| 66_Services | `#1565C0` | Blue |
| 67_Orgs | `#00838F` | Teal |

設定後、再起動しても保持されます（Obsidian 自身が graph.json に書き出すため）。

---

## 📝 既存ページへの `cssclasses` 一括追加（任意）

タイトル色も全ページに反映させたい場合、frontmatter に `cssclasses: [layer-*]` を追加する必要があります。79ページあるため、必要に応じて段階的に、または自動スクリプトで対応してください。

### 自動追加スクリプト例（Python）

```python
#!/usr/bin/env python3
"""既存ページの frontmatter に cssclasses を追加"""
import frontmatter
from pathlib import Path

VAULT = Path("/Users/k-kawahara/Obsidian/my-skill-graph")

TYPE_TO_CLASS = {
    "law": "layer-law",
    "guideline": "layer-guideline",
    "framework": "layer-framework",
    "disorder": "layer-disorder",
    "method": "layer-method",
    "assessment": "layer-assessment",
    "service": "layer-service",
    "org": "layer-org",
    "person": "layer-person",
    "moc": "layer-moc",
    "insight": "layer-insight",
    "meta": "layer-meta",
}

for md in VAULT.rglob("*.md"):
    if ".obsidian" in md.parts or "raw" in md.parts or ".claude" in md.parts:
        continue
    post = frontmatter.load(md)
    t = post.get("type")
    if t and t in TYPE_TO_CLASS:
        existing = post.get("cssclasses", [])
        if TYPE_TO_CLASS[t] not in existing:
            existing.append(TYPE_TO_CLASS[t])
            post["cssclasses"] = existing
            md.write_text(frontmatter.dumps(post), encoding="utf-8")
            print(f"updated: {md}")
```

依存: `pip install python-frontmatter`

実行前に vault をバックアップ推奨。

---

## ✅ チェックリスト

セットアップ完了時に以下を確認:

- [ ] Obsidian を完全再起動した
- [ ] `.obsidian/graph.json` の colorGroups に14エントリある
- [ ] 設定 → 外観 → CSS snippets で `layer-colors` がON
- [ ] ファイルエクスプローラーのフォルダ名が色付け
- [ ] グラフビューを開くと層ごとに色分け
- [ ] Cmd+Q で終了 → 再起動しても色が保持される
