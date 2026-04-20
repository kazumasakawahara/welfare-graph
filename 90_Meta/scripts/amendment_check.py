#!/usr/bin/env /usr/bin/python3
"""
amendment_check.py
法令・ガイドライン・サービス報酬の改正追随状況をチェックする。

チェック項目:
  1. review_due 期限近接/超過
  2. version_hash ドリフト（monitoring_url の現在ハッシュと保存済ハッシュを比較）
  3. last_verified からの経過日数
  4. archived/ フォルダの整合性（superseded_by 欠損）
  5. pending-amendment ステータス滞留

出力:
  90_Meta/amendment-reports/{YYYY-MM-DD}.md
"""

import hashlib
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    import frontmatter
except ImportError:
    print("pip install python-frontmatter が必要", file=sys.stderr)
    sys.exit(1)

VAULT = Path(__file__).resolve().parents[2]
REPORT_DIR = VAULT / "90_Meta" / "amendment-reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 監視対象層
MONITORED_LAYERS = {"60_Laws", "61_Guidelines", "66_Services"}

# 期限近接の閾値（日）
DUE_SOON_DAYS = 90       # 3 か月以内で警告
DUE_CRITICAL_DAYS = 30   # 1 か月以内で重大

# last_verified の陳腐化閾値
STALE_VERIFIED_DAYS = 365  # 1 年以上未確認で警告

# HTTP リクエスト設定
HTTP_TIMEOUT = 10
HTTP_USER_AGENT = "welfare-graph-amendment-check/1.0"


def today() -> date:
    return date.today()


def load_fm_safely(md_path: Path):
    """HTML コメント <!-- allow-realname --> を除去してから frontmatter パース"""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    clean = lines[:]
    while clean and (clean[0].strip().startswith("<!--") or clean[0].strip() == ""):
        clean.pop(0)
    cleaned = "\n".join(clean)
    try:
        post = frontmatter.loads(cleaned)
    except Exception as e:
        return None, content, str(e)
    return post, content, None


def parse_date(v):
    if isinstance(v, (date, datetime)):
        return v if isinstance(v, date) else v.date()
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def fetch_url_hash(url: str) -> tuple:
    """URL を取得し、SHA256 ハッシュの先頭 8 桁を返す。(hash, error_message)"""
    if not url:
        return None, "URL 未設定"
    try:
        req = Request(url, headers={"User-Agent": HTTP_USER_AGENT})
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            body = resp.read()
            h = hashlib.sha256(body).hexdigest()[:8]
            return h, None
    except URLError as e:
        return None, f"接続失敗: {e.reason}"
    except Exception as e:
        return None, f"取得エラー: {type(e).__name__}"


def iter_monitored_notes():
    """監視対象層のノートを yield"""
    for layer in MONITORED_LAYERS:
        layer_dir = VAULT / layer
        if not layer_dir.exists():
            continue
        for md in layer_dir.rglob("*.md"):
            # archived/ 配下は別扱い
            if "archived" in md.parts:
                continue
            if md.stem == "README":
                continue
            yield md, layer


def iter_archived_notes():
    """archived/ 配下のノートを yield"""
    for layer in MONITORED_LAYERS:
        archived_dir = VAULT / layer / "archived"
        if not archived_dir.exists():
            continue
        for md in archived_dir.rglob("*.md"):
            yield md, layer


def check_review_due(meta: dict, rel_path: str) -> tuple:
    """review_due の状態を判定し (severity, message) を返す"""
    rd = parse_date(meta.get("review_due"))
    if not rd:
        return None, None

    today_d = today()
    delta = (rd - today_d).days

    if delta < 0:
        return "critical", f"review_due 超過 {-delta} 日 ({rd})"
    elif delta <= DUE_CRITICAL_DAYS:
        return "critical", f"review_due 残り {delta} 日 ({rd})"
    elif delta <= DUE_SOON_DAYS:
        return "warning", f"review_due 残り {delta} 日 ({rd})"
    return None, None


def check_last_verified(meta: dict) -> tuple:
    """last_verified の鮮度を判定"""
    lv = parse_date(meta.get("last_verified"))
    if not lv:
        return "info", "last_verified 未設定（設定推奨）"

    days_since = (today() - lv).days
    if days_since > STALE_VERIFIED_DAYS:
        return "warning", f"last_verified から {days_since} 日経過（要再検証）"
    return None, None


def check_version_hash_drift(meta: dict, online: bool = False) -> tuple:
    """
    monitoring_url を取得し version_hash と比較

    online=False の場合はスキップ（API 制限・ネットワーク問題時用）
    """
    mon_url = meta.get("monitoring_url")
    stored_hash = meta.get("version_hash")

    if not mon_url:
        if not stored_hash:
            return "info", "monitoring_url, version_hash 未設定"
        return None, None

    if not online:
        return None, None

    current_hash, err = fetch_url_hash(mon_url)
    if err:
        return "info", f"version_hash 取得失敗: {err}"

    if not stored_hash:
        return "warning", f"version_hash 未設定（現在値: {current_hash}）"

    if current_hash != stored_hash:
        return "critical", f"version_hash ドリフト検知: {stored_hash} → {current_hash}（改正可能性）"

    return None, None


def check_status_stuck(meta: dict) -> tuple:
    """status: pending-amendment が長期滞留していないか"""
    status = meta.get("status", "active")
    if status != "pending-amendment":
        return None, None

    updated = parse_date(meta.get("updated"))
    if not updated:
        return "info", "status=pending-amendment だが updated が未設定"

    days_pending = (today() - updated).days
    if days_pending > 90:
        return "warning", f"pending-amendment 滞留 {days_pending} 日（差分統合を検討）"
    return None, None


def check_archived_integrity(meta: dict) -> tuple:
    """archived/ 配下のノートに superseded_by があるか"""
    status = meta.get("status")
    if status != "archived":
        return "warning", "archived/ 配下だが status が 'archived' ではない"

    superseded_by = meta.get("superseded_by")
    if not superseded_by:
        return "critical", "archived/ 配下だが superseded_by が未設定"

    return None, None


def run_checks(online: bool = False):
    critical = []
    warning = []
    info = []
    stats = {
        "monitored": 0,
        "archived": 0,
        "pending_amendment": 0,
        "with_monitoring_url": 0,
        "with_version_hash": 0,
    }

    # 現行ノートのチェック
    for md, layer in iter_monitored_notes():
        rel = str(md.relative_to(VAULT))
        post, _, err = load_fm_safely(md)
        if err or not post or not post.metadata:
            continue

        meta = post.metadata
        stats["monitored"] += 1
        if meta.get("monitoring_url"):
            stats["with_monitoring_url"] += 1
        if meta.get("version_hash"):
            stats["with_version_hash"] += 1
        if meta.get("status") == "pending-amendment":
            stats["pending_amendment"] += 1

        # 各チェック実行
        for check_fn, *args in [
            (check_review_due, meta, rel),
            (check_last_verified, meta),
            (check_version_hash_drift, meta, online),
            (check_status_stuck, meta),
        ]:
            try:
                severity, msg = check_fn(*args)
            except TypeError:
                continue
            if severity == "critical":
                critical.append((rel, msg))
            elif severity == "warning":
                warning.append((rel, msg))
            elif severity == "info":
                info.append((rel, msg))

    # archived/ 配下のチェック
    for md, layer in iter_archived_notes():
        rel = str(md.relative_to(VAULT))
        post, _, err = load_fm_safely(md)
        if err or not post or not post.metadata:
            continue

        stats["archived"] += 1
        severity, msg = check_archived_integrity(post.metadata)
        if severity == "critical":
            critical.append((rel, msg))
        elif severity == "warning":
            warning.append((rel, msg))

    return critical, warning, info, stats


def generate_report(critical, warning, info, stats, online):
    today_d = today()
    lines = []
    R = lines.append

    R("<!-- allow-realname -->")
    R("---")
    R("type: meta")
    R("tags: [meta, amendment-report]")
    R(f"generated_at: {today_d.isoformat()}")
    R("cssclasses: [layer-meta]")
    R("---")
    R("")
    R(f"# 改正追随レポート {today_d.isoformat()}")
    R("")
    R(f"**オンライン検証**: {'有効' if online else '無効（ハッシュ比較スキップ）'}")
    R("")
    R("## 📊 統計")
    R("")
    R(f"- 現行監視ノート: {stats['monitored']}")
    R(f"- アーカイブノート: {stats['archived']}")
    R(f"- pending-amendment 中: {stats['pending_amendment']}")
    R(f"- monitoring_url 設定済: {stats['with_monitoring_url']} / {stats['monitored']}")
    R(f"- version_hash 設定済: {stats['with_version_hash']} / {stats['monitored']}")
    R("")
    R(f"## 🔴 CRITICAL ({len(critical)} 件)")
    R("")
    if critical:
        for path, msg in critical:
            R(f"- `{path}`: {msg}")
    else:
        R("なし")
    R("")
    R(f"## 🟡 WARNING ({len(warning)} 件)")
    R("")
    if warning:
        for path, msg in warning:
            R(f"- `{path}`: {msg}")
    else:
        R("なし")
    R("")
    R(f"## 🟢 INFO ({len(info)} 件)")
    R("")
    if info:
        for path, msg in info:
            R(f"- `{path}`: {msg}")
    else:
        R("なし")
    R("")
    R("## 🎯 推奨アクション")
    R("")
    if critical:
        R("### 緊急対応")
        R("- [ ] CRITICAL 項目を e-Gov / 厚労省で一次確認")
        R("- [ ] 改正が確認できたら `status: pending-amendment` に変更")
        R("- [ ] `raw/laws/` に原文配置 → `law-amendment-integrate` スキル実行")
        R("")
    if warning:
        R("### 今月中の対応")
        R("- [ ] WARNING 項目の `last_verified` 更新")
        R("- [ ] `monitoring_url` 未設定ノートの URL 追加")
        R("")
    if stats["with_monitoring_url"] < stats["monitored"]:
        missing = stats["monitored"] - stats["with_monitoring_url"]
        R(f"### データ充実")
        R(f"- [ ] monitoring_url 未設定 {missing} 件の補完")
        R("")
    R("---")
    R("")
    R("改正追随の運用設計は [[90_Meta/amendment-tracking]] を参照。")
    return "\n".join(lines)


def main():
    online = "--online" in sys.argv
    print(f"vault: {VAULT}")
    print(f"オンライン検証: {'有効' if online else '無効'}")
    print("改正追随チェック実行中...")

    critical, warning, info, stats = run_checks(online=online)
    report = generate_report(critical, warning, info, stats, online)

    out_path = REPORT_DIR / f"{today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")

    print()
    print("✅ 改正追随レポート生成完了")
    print(f"  出力: {out_path.relative_to(VAULT)}")
    print(f"  CRITICAL: {len(critical)}")
    print(f"  WARNING:  {len(warning)}")
    print(f"  INFO:     {len(info)}")
    print(f"  監視対象: {stats['monitored']} ノート")


if __name__ == "__main__":
    main()
