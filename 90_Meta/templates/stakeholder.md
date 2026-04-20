---
type: stakeholder
id: X-XXXX            # F-/O-/M-/G-/S-/C-/N- のいずれか
category: ""          # 家族 / 事業所 / 医療 / 後見 / 社協 / 相談支援 / その他
relation_to: []       # [[P-XXXX]] 関係する当事者
role_description: ""
contact: ""           # 担当者名（仮名）・連絡方法
status: active        # active / inactive / transitioning
created: {{date}}
updated: {{date}}
tags: [stakeholder]
cssclasses: [layer-stakeholder]
---

# {{title}}

## 役割・関与内容


## 担当している CareRole
<!-- 親亡き後設計に関わる機能があれば明記 -->
-

## 特記事項 / 暗黙知
<!-- この関係者との付き合い方、過去のトラブル、強み等 -->


## 関連エピソード
```dataview
LIST
FROM "20_Episodes"
WHERE contains(file.outlinks, this.file.link)
SORT file.name DESC
LIMIT 10
```
