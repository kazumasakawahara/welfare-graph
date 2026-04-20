<!-- allow-realname -->
# CONTRIBUTING — welfare-graph への貢献ガイド

welfare-graph は **進化する知識グラフ** を目指しています。法令改正・新ガイドライン・新サービス・現場知見の蓄積は、相談支援専門員コミュニティの集合知で支えられます。

## 🌱 どんな貢献を歓迎するか

| カテゴリ | 例 |
|---|---|
| **法令改正の反映** | 報酬改定・法改正・告示改定の追記 |
| **ガイドライン更新** | 厚労省・自治体の新規/改訂ガイドラインの取り込み |
| **サービス情報追加** | 新設サービス・廃止情報・運用変更 |
| **障害特性・支援技法** | 新しい知見・エビデンス更新 |
| **判例・事例（公知）** | 重要判例・象徴的事例（個人特定不可形式で） |
| **誤情報修正** | 既存ノートの誤り・古い情報の指摘 |
| **スキーマ・スクリプト改善** | バリデーション強化・新しい運用支援機能 |
| **翻訳・ローカライズ** | 多言語対応（将来） |

## 🚫 受け付けないもの

- **特定個人を識別できる情報**（実名・電話番号・住所等）
- **未公開・未告知の情報**（一次ソース URL がない情報）
- **特定事業者を批判する内容**（公的批判は認めるが個別事業者攻撃は不可）
- **支援者を装った勧誘・宣伝**

## 🛠 貢献の流れ

### A. 軽微な修正（誤字・リンク切れ・1 行修正）

1. GitHub 上で直接 **Edit** ボタンから修正
2. PR を作成（自動でテンプレートが表示される）
3. メンテナがレビュー → マージ

### B. ノート 1 件分の追加・更新

1. リポジトリを Fork
2. 新規ブランチ作成: `feat/{法令名}-{年}` または `fix/{ノート名}`
3. ノートを追加 / 編集
4. ローカルで品質チェック実行:
   ```bash
   /usr/bin/python3 90_Meta/scripts/vault_health_check.py
   /usr/bin/python3 90_Meta/scripts/amendment_check.py
   ```
5. CRITICAL/WARNING がないことを確認
6. PR 作成（テンプレートに従って記入）

### C. 大規模変更（スキーマ拡張・新スキル・複数層に渡る変更）

1. **先に Issue で議論**: `proposal:` プレフィックスで Issue を立てる
2. メンテナと方向性を合意
3. 実装ブランチで開発
4. PR 作成

## 📝 コミットメッセージ規約

[Conventional Commits](https://www.conventionalcommits.org/) を採用:

```
<type>(<scope>): <subject>

<body (optional)>

<footer (optional)>
```

### 例

```
feat(law): 障害者総合支援法 令和9年改正対応

- archived/ に旧版を退避
- 就労選択支援の運用要綱を反映
- 影響を受ける P-XXXX ノードの relations を再評価

一次ソース: https://www.mhlw.go.jp/...
施行日: 2027-04-01

Co-Authored-By: 相談支援専門員X <noreply@example.com>
```

### type 一覧

| type | 用途 |
|---|---|
| `feat` | 新規ノート・新機能 |
| `fix` | 誤情報修正・バグ修正 |
| `docs` | README/USER_GUIDE 等 |
| `refactor` | スキーマ変更・relations 整理 |
| `chore` | 依存更新・運用作業 |
| `style` | CSS・配色 |
| `test` | チェックスクリプト・健全性 |

### scope 一覧

| scope | 対象 |
|---|---|
| `law` | 60_Laws/ |
| `guideline` | 61_Guidelines/ |
| `service` | 66_Services/ |
| `disorder` | 63_Disorders/ |
| `method` | 64_Methods/ |
| `org` | 67_Orgs/ |
| `meta` | 90_Meta/ |
| `skill` | .claude/skills/ |
| `script` | 90_Meta/scripts/ |
| `moc` | 00_MOC/ |

## ✅ 必須チェックリスト（PR 提出前）

### すべての PR

- [ ] `vault_health_check.py` が CRITICAL 0 件
- [ ] 実名・電話番号が含まれていない（自動 hook で検査される）
- [ ] frontmatter の必須フィールドが埋まっている

### ノート追加・更新の PR

- [ ] `source_url` に一次情報の URL を記載
- [ ] `version`, `effective_date`, `review_due` を設定
- [ ] `last_verified` に確認日を記載
- [ ] `relations` に最低 2 件の関連ノートへのリンク
- [ ] cssclasses に該当 layer-xxx を設定

### 改正対応の PR

- [ ] 旧版を `archived/` に退避（破壊的変更でない場合）
- [ ] 新版に `amendment_history` エントリ追加
- [ ] `supersedes` / `superseded_by` 相互リンク
- [ ] 影響を受けるノートの relations をレビュー

### スキーマ・スクリプト変更の PR

- [ ] 90_Meta/SCHEMA.md の更新
- [ ] 後方互換性の検討（既存ノートに影響しないか）
- [ ] sync_to_neo4j.py の動作確認（必要なら）

## 🔐 セキュリティ・プライバシー

### 禁止事項

- **実名の混入**: hook で自動検知されるが、意図的バイパス禁止
- **要配慮個人情報**: 病名・診断名と個人を結びつける記述
- **未公表情報**: 公式発表前の改正情報・内部通知

### 推奨事項

- **GPG/SSH コミット署名**: 真正性保証のため
- **Co-Authored-By**: 共同作業時は明示
- **pre-commit hook 利用**: ローカルで `.claude/hooks/realname_detect.py` を活用

## 🎯 レビュー基準

メンテナは以下を確認します:

| 観点 | 確認内容 |
|---|---|
| **一次情報整合性** | source_url が実在し、内容が一致するか |
| **実名混入なし** | hook 通過 + 目視確認 |
| **スキーマ準拠** | SCHEMA.md に従った frontmatter |
| **relations 妥当性** | 関連先ノートが実在し、type と weight が適切 |
| **重複なし** | 既存ノートと重複していないか |
| **可読性** | 相談支援専門員が理解できる文体 |
| **中立性** | 特定事業者・主義の宣伝になっていないか |

## 🤝 コミュニティ規範

- **建設的に**: 批判ではなく改善提案として
- **多様性を尊重**: 地域・領域・経験年数の違いを前提に
- **本人視点**: 当事者・家族の利益を最優先
- **学び合い**: 質問は歓迎、丁寧に応答する
- **継続性**: 一度の貢献より、継続的な関与を歓迎

## 📞 困った時は

- **GitHub Issues**: 質問・バグ報告・機能要望
- **GitHub Discussions** (将来): 雑談・運用相談
- **Pull Request コメント**: レビュー上の議論

## 🏆 貢献者への謝意

すべての貢献者は `CONTRIBUTORS.md`（自動生成）に記載されます。

- 法令改正対応の主要貢献者は README に明記
- 大規模スキーマ拡張は `90_Meta/CHANGELOG.md` で言及
- 年間貢献量上位者は GitHub Releases ノートで紹介

## 📜 ライセンス

貢献いただいた内容は以下のライセンスで配布されます（Inbound = Outbound）:

- **コード（Python・CSS等）**: MIT License
- **ドキュメント・ノート（Markdown）**: CC BY-SA 4.0

PR 提出 = ライセンス条件への同意とみなします。

---

**3 年続ければ、地域の支援知識の共有資産になります。** ゆっくり、確実に、共に育てていきましょう。
