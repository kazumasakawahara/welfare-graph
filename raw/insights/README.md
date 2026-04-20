<!-- allow-realname -->
# raw/insights/

事例・判例・ナラティブ・Wikipedia 記事等を保管する場所。
取り込み先は **`30_Insights/`**（または内容により他層）。

## 命名規則

```
raw/insights/{年月またはYYYY}_{事件名・事例名}.{ext}
```

例:
- `raw/insights/2003_七生養護学校事件.md`
- `raw/insights/2024-07_旧優生保護法違憲判決.md`
- `raw/insights/2025-03_地域A自立支援協議会_事例検討.md`

## 取り込み手順

詳細は [`raw/README.md`](../README.md) または [`docs/USER_GUIDE.md`](../../docs/USER_GUIDE.md) 参照。

簡略フロー:
1. 資料をこのフォルダに配置
2. Claude Code に「raw/insights/xxx を 30_Insights に取り込んで」と指示
3. 自動で要約・構造化された Insight ページが生成される
4. レビューして必要なら修正
