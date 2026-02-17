# Discord Webhook パターン（SCOUT SYSTEM向け）

## 基本送信パターン
```python
import httpx


def send_discord(webhook_url: str, message: str) -> None:
    if not webhook_url:
        return
    httpx.post(webhook_url, json={"content": message}, timeout=10)
```

## 2000文字制限の分割送信
```python
MAX_LEN = 2000


def split_report(text: str) -> list[str]:
    if len(text) <= MAX_LEN:
        return [text]

    chunks = []
    buffer = ""
    for section in text.split("\n\n"):
        candidate = section if not buffer else f"{buffer}\n\n{section}"
        if len(candidate) <= MAX_LEN:
            buffer = candidate
        else:
            if buffer:
                chunks.append(buffer)
            buffer = section
    if buffer:
        chunks.append(buffer)
    return chunks
```

- 分割は `TOP10 / HOT10 / WATCHLIST` などのセクション境界を優先

## 通知フォーマット実装
```python
def format_report(run_summary, top10, hot10, watchlist, trends) -> str:
    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🔍 SCOUT REPORT | {run_summary['timestamp_jst']}")
    lines.append(f"Type: {run_summary['run_type']} | Scanned: {run_summary['scanned']} | Hot Threshold: {run_summary['hot_threshold']}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    lines.append("🏆 TOP 10")
    for i, item in enumerate(top10, 1):
        lines.append(f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})")

    lines.append("\n🔥 HOT 10  (85+・急上昇)")
    top_ids = {t['entity_id'] for t in top10}
    for i, item in enumerate(hot10, 1):
        if item['entity_id'] in top_ids:
            lines.append(f"{i}. @{item['display_name']}  ↑ Top参照")
        else:
            lines.append(f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})")

    lines.append("\n👀 WATCHLIST")
    for i, item in enumerate(watchlist, 1):
        lines.append(f"{i}. @{item['display_name']}  ⭐{item['total_score']}  ({item['score_delta']:+d})")

    lines.append("\n📈 TREND KEYWORDS")
    lines.append("7d burst : " + ", ".join(t['keyword'] for t in trends.get('7d', [])))
    lines.append("30d growth: " + ", ".join(t['keyword'] for t in trends.get('30d', [])))
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)
```

## Top/Hot 重複エンティティ
- `top` の `entity_id` 集合を先に作る
- `hot` 側で重複したら `↑ Top参照` を表示する

## エラーハンドリング
```python
def safe_send_discord(webhook_url: str, message: str, logger) -> None:
    if not webhook_url:
        logger.info("discord webhook is not configured; skip")
        return
    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(webhook_url, json={"content": message})
            r.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"discord notify failed: {e}")
```

- Webhook未設定はスキップ（通知は任意）
- 4xx/5xx はログに残して処理継続（通知失敗で run を止めない）

## テスト方法
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"SCOUT webhook test"}'
```
