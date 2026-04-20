<!-- allow-realname -->
# raw/services/

サービス報酬告示・通知・運営基準などの原本を保管。
取り込み先は **`66_Services/`**。

## 命名規則

```
raw/services/{サービス名}_{版名}.pdf
```

例:
- `raw/services/行動援護_令和6年度報酬告示.pdf`
- `raw/services/共同生活援助_運営基準.pdf`

## 取り込み時の確認項目

- `service_name`: サービス名
- `law_basis`: 根拠法（[[60_Laws/障害者総合支援法]] 等）
- `target`: 対象者要件
- `fee_code`: 報酬告示コード
- `version`: 報酬改定年度
- `review_due`: 次回報酬改定予定（原則3年後）

## 取り込み手順

詳細は [`raw/README.md`](../README.md) 参照。
