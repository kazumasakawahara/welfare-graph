<!-- allow-realname -->
# welfare-graph ドキュメント

相談支援専門員向けのドキュメント一覧です。

## 📖 メインドキュメント

### 🚀 [QUICKSTART.md](QUICKSTART.md) — 15 分クイックスタート
まず中身を見てみたい方向け。最短でセットアップして眺めるところまで。

### 📖 [USER_GUIDE.md](USER_GUIDE.md) — 使用説明書（完全版）
業務で本格的に使う方向けの 15 章構成。
Obsidian 未経験・プログラミング未経験の方でも順番に進めれば使えるようになります。

### ❓ [FAQ.md](FAQ.md) — よくある質問
トラブルシューティング・ライセンス・複数人運用など。

## 🎨 設定ドキュメント（プロジェクト内）

- [../90_Meta/SCHEMA.md](../90_Meta/SCHEMA.md) — frontmatter 仕様・リンク型辞書
- [../90_Meta/SETUP_COLORS.md](../90_Meta/SETUP_COLORS.md) — 彩色システムのセットアップ詳細
- [../90_Meta/neo4j-integration-design.md](../90_Meta/neo4j-integration-design.md) — Neo4j 連携の設計書（上級者向け）

## 🛠️ スキル（Claude Code 連携・任意）

各スキルの使い方は `.claude/skills/` 内の各 `SKILL.md` を参照:

- `support-hypothesis` — 根拠付き支援仮説の自動生成
- `vault-health-check` — vault の健全性診断
- `ecomap-from-relations` — Mermaid エコマップ自動生成
- `visit-prep` — 訪問前ブリーフィング生成
- `monthly-summary` — 月次モニタリングサマリ生成
- `realname-check` — 実名混入の監査

## 💬 サポート

- **バグ報告・機能要望**: [GitHub Issues](https://github.com/kazumasakawahara/welfare-graph/issues)
- **改善提案（Pull Request）**: 大歓迎です
