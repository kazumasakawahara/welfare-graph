---
name: visit-prep
description: 訪問・面談の前に、対象当事者（P-XXXX）の情報を vault から集約し、簡潔なブリーフィングシートを生成する。禁忌事項→推奨ケア→直近エピソード→CareRole/代替手段の進捗→次回確認事項の順でまとめる。相談支援専門員が訪問直前に使う想定。
---

<!-- allow-realname -->


# visit-prep skill

## 用途
訪問・面談の前に、対象当事者の最新情報を数分で把握するためのブリーフィングを生成する。

## 入力
- 当事者ID（必須）: 例 `P-0001`
- 訪問目的（任意）: モニタリング / 計画相談 / 緊急対応 / etc
- 同席予定者（任意）: F-0001, O-0001 等

## 出力フォーマット

```markdown
# 訪問ブリーフィング: {P-XXXX}

**生成日時**: {YYYY-MM-DD HH:MM}
**訪問目的**: {目的}
**同席予定**: {関係者}

---

## 🚨 禁忌・注意事項（最優先）
- （10_People の Contraindications から抽出）

## ✅ 推奨ケア
- （10_People の Preferred Care から抽出）

## 📋 基本情報スナップショット
- 診断: ...
- 居住: ...
- 主たる支援者: ...

## 📅 直近エピソード（過去30日・重大度順）
1. [日付] [重大度] 概要（→ 詳細: [[ファイル]]）
2. ...

## 🕸️ 親亡き後設計の進捗
- 高リスク CareRole（代替未検討・検討中）:
  - {role}: 担い手 {holder}, 代替 {plan} ({status})
- 契約準備中 / 稼働中の Substitute:
  - {provider_type}: {status}

## ❓ 今回の訪問で確認すべき事項
- 前回エピソードの follow-up:
- CareRole 移行に関する本人・家族の意向確認:
- その他（AI が文脈から提案）:

## 🔗 関連知見
- [[insight-A]]: 適用のヒント
- [[insight-B]]: ...
```

## 実行手順（Claude 向け）

1. **対象ノートを読む**
   - `10_People/{id}.md` を Read
   - frontmatter から diagnosis / disability_cert / primary_supporter を取得

2. **エピソード収集**
   - `20_Episodes/` から `{id}` を含むファイル名を Glob
   - 過去30日分（`date` フィールドでフィルタ）を Read
   - severity で並べ替え、high/critical を先頭に

3. **CareRole / Substitute**
   - `50_Resilience/CareRoles/` から `{id}_` プレフィックスのファイルを Glob
   - risk_level と substitute_status を一覧化
   - `50_Resilience/Substitutes/` も同様に取得

4. **関連 Insight**
   - `30_Insights/` を Grep で `[[{id}]]` または対象エピソードへのリンクを持つものを検索

5. **ブリーフィング生成**
   - 上記フォーマットに従って markdown を出力
   - 本文に実名が入り込まないよう仮名IDのみ使用

6. **保存場所（任意）**
   - ユーザーが保存を望む場合: `20_Episodes/briefings/{YYYY-MM-DD}_{id}_brief.md`
   - デフォルトは標準出力のみ

## 注意事項
- 実名は一切出力しない（alias_map は参照しない）
- エピソードが存在しない場合は「記録なし」と明示
- 禁忌事項が未記入の場合は警告を出す
