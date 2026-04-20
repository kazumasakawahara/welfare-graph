---
type: moc
tags: [moc, home]
cssclasses: [layer-moc]
---

# Home

知的障害のある方の支援知識グラフへようこそ。

## ナビゲーション
- [[People]] - 当事者一覧
- [[Themes]] - 知見テーマ一覧
- [[Timeline]] - エピソード時系列
- [[Resilience]] - 親亡き後設計
- [[Knowledge]] - **知識層（法令・ガイドライン・サービス・技法等）**
- [[Sexuality]] - 性と教育のテーマ別ハブ

## 運用の基本
1. 初回面接で [[10_People/]] に人物ノート作成
2. 関係者を [[40_Stakeholders/]] に登録
3. 訪問・面談のたびに [[20_Episodes/]] にエピソード追加
4. 親が担う機能を [[50_Resilience/CareRoles/]] で棚卸し
5. パターンが見えたら [[30_Insights/]] に知見として昇華
6. 人物ノートから [[Knowledge]] 層へ `relations` で根拠リンク

## 仮名化
すべてのノートで仮名IDを使用。実名マップは `90_Meta/alias_map.md`（Meld Encryptで暗号化）。
詳細は [[README]] 参照。

## 未処理タスク
```dataview
TASK
FROM ""
WHERE !completed
GROUP BY file.link
LIMIT 20
```
