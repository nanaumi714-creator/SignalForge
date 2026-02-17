# YouTube Data API v3 パターン（SCOUT SYSTEM向け）

## セットアップ
```bash
pip install google-api-python-client
```

```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def build_youtube_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key)
```

## パターン1: キーワード検索（search.list）
```python
def search_channels(youtube, keyword: str, max_results: int = 12, lang: str = "en") -> list[str]:
    resp = (
        youtube.search()
        .list(
            q=keyword,
            part="snippet",
            type="channel",
            maxResults=max_results,
            relevanceLanguage=lang,
        )
        .execute()
    )
    return [item["snippet"]["channelId"] for item in resp.get("items", [])]
```

- 主要パラメータ: `q / part / type / maxResults / relevanceLanguage`
- `channel_id` 抽出: `item["snippet"]["channelId"]`
- quota コスト: **100 / 回**

## パターン2: チャンネル詳細取得（channels.list）
```python
def get_channel_details(youtube, channel_ids: list[str]) -> list[dict]:
    if not channel_ids:
        return []

    resp = (
        youtube.channels()
        .list(
            id=",".join(channel_ids[:50]),
            part="snippet,statistics",
            maxResults=50,
        )
        .execute()
    )
    return resp.get("items", [])
```

- 最大50件を `id=",".join(ids)` で一括取得
- `part="snippet,statistics"` で取得できる代表情報:
  - display_name (`snippet.title`)
  - description (`snippet.description`)
  - subscribers (`statistics.subscriberCount`)
  - total_views (`statistics.viewCount`)
- quota コスト: **1 / 回**

## パターン3: 直近動画取得（search.list + channelId）
```python
def get_recent_videos(youtube, channel_id: str, n: int = 10) -> list[dict]:
    resp = (
        youtube.search()
        .list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=n,
        )
        .execute()
    )
    return [
        {
            "video_id": item["id"].get("videoId"),
            "title": item["snippet"].get("title"),
            "published_at": item["snippet"].get("publishedAt"),
        }
        for item in resp.get("items", [])
    ]
```

- `order="date"` で新しい順
- quota コスト: **100 / 回**

## Quota 管理表
| API | quota/回 | 1 run での推奨上限 |
|---|---:|---:|
| search.list (keyword/channel search) | 100 | 5回以内 |
| channels.list | 1 | 10回以内 |

> 無料枠 10,000/日を基準に、search系の回数を優先的に制御する。

## エラーハンドリング
```python
import time
from googleapiclient.errors import HttpError


def with_youtube_error_handling(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except HttpError as e:
        status = getattr(e, "status_code", None) or getattr(e.resp, "status", None)
        if status == 403:
            raise RuntimeError("YouTube quota exceeded")
        if status == 404:
            return None  # channel not found -> skip
        time.sleep(1)
        return fn(*args, **kwargs)  # retry 1
```

- `403`: quota超過として処理中断 + エラーログ
- `404`: チャンネル非存在としてスキップ
- その他: retry 1回後にスキップ

## このプロジェクトでの使われ方
- Phase 2 の `worker/collector.py` で使用
- Phase 6 の Trend派生収集でも使用
