# Supabase CRUD パターン（SCOUT SYSTEM向け）

## クライアント初期化
```python
# db/client.py
from supabase import Client, create_client
from config import get_settings

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        s = get_settings()
        _client = create_client(s.supabase_url, s.supabase_key)
    return _client
```

## INSERT パターン
```python
def insert_run(run_type: str, config: dict) -> str:
    sb = get_supabase()
    resp = sb.table("scout_runs").insert({"run_type": run_type, "config": config}).execute()
    return resp.data[0]["id"]
```

## UPSERT パターン（重要）
```python
def upsert_entity(platform: str, platform_id: str, payload: dict) -> str:
    sb = get_supabase()
    row = {
        "platform": platform,
        "platform_id": platform_id,
        **payload,
    }
    resp = (
        sb.table("scout_entities")
        .upsert(row, on_conflict="platform,platform_id")
        .execute()
    )
    return resp.data[0]["id"]
```

- `UNIQUE(platform, platform_id)` を前提に upsert する

## SELECT パターン
```python
def get_scores_by_run(run_id: str):
    sb = get_supabase()
    return (
        sb.table("scout_scores")
        .select("*, scout_entities(*)")
        .eq("run_id", run_id)
        .order("total_score", desc=True)
        .execute()
        .data
    )
```

- 基本: `select / eq / order`
- JOIN相当: `select("*, scout_entities(*)")`

## UPDATE パターン
```python
def update_run_status(run_id: str, status: str, summary: dict | None = None):
    sb = get_supabase()
    payload = {"status": status}
    if summary is not None:
        payload["summary"] = summary
    sb.table("scout_runs").update(payload).eq("id", run_id).execute()
```

## このプロジェクト固有の注意点
- 外部キー順序: `runs -> entities -> snapshots -> scores`
- DBアクセスは `db/queries.py` に集約（直接クライアント禁止）
- UUID は DB の `gen_random_uuid()` で生成する

## よくあるエラーと対処
- `23505 (UNIQUE違反)`: insert ではなく upsert を使う
- `23503 (FK違反)`: insert順序を確認する
- タイムゾーン: `TIMESTAMPTZ` はUTCで保存し、表示時にJSTへ変換する
