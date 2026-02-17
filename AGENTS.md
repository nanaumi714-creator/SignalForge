# AGENTS.md

## Project Overview
SCOUT SYSTEM は、海外クリエイター（VTuber / Cover / 配信者）を対象とした市場調査エンジンです。
週次実行 + 任意実行で、候補抽出・スコアリング・トレンド分析・通知を行います。
AI駆動開発で、コンテキスト整備→ドキュメント→実装の順で進めます。

## Tech Stack
| Component | Version | Role |
|---|---:|---|
| Python | 3.11+ | 実装言語 |
| FastAPI | >=0.111.0 | APIサーバー |
| Uvicorn | >=0.29.0 | ASGI実行 |
| Supabase Python | >=2.4.0 | PostgreSQLアクセス |
| OpenAI Python | >=1.30.0 | GPT分析/トレンド抽出 |
| google-api-python-client | >=2.130.0 | YouTube Data API v3 |
| httpx | >=0.27.0 | Discord Webhook送信 |
| pydantic / pydantic-settings | >=2.7.0 / >=2.2.0 | スキーマ/設定管理 |
| python-dotenv | >=1.0.0 | ローカル環境補助 |

## Directory Layout
```text
scout/
├── main.py                  # FastAPI entrypoint / router registration
├── config.py                # Environment variables via pydantic-settings only
├── requirements.txt         # Python dependencies
├── .env                     # Local secrets (do not commit)
│
├── api/
│   ├── runs.py              # POST/GET /v1/scout/runs*
│   ├── pins.py              # POST/DELETE /v1/scout/pins*
│   └── commands.py          # POST /v1/scout/commands
│
├── worker/
│   ├── orchestrator.py      # End-to-end run pipeline control
│   ├── collector.py         # YouTube collection logic
│   ├── analyzer.py          # GPT scoring / trend extraction
│   ├── scorer.py            # top/hot/watch/normal classification
│   └── notifier.py          # Discord report formatting/sending
│
├── db/
│   ├── client.py            # Supabase singleton client
│   └── queries.py           # All DB operations centralization
│
├── models/
│   └── schemas.py           # Pydantic schemas (API + worker I/O)
│
└── supabase/
    └── migrations/
        └── 001_init.sql     # Initial table definitions
```

## Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
curl -X POST http://localhost:8000/v1/scout/runs -H "Content-Type: application/json" -d '{"run_type":"manual","notify_discord":false}'
```

## Coding Rules（最重要）
- DB操作は `db/queries.py` に集約（直接 supabase クライアントを叩かない）
- GPT呼び出しはバッチ5件ずつ（レート制限対策）
- スコアは Pydantic バリデーション後にDBへ保存
- 環境変数は `config.py` 経由でのみ読む（`.env` 直読み禁止）
- 例外はすべて `try/except` で捕捉しログに残す
- 新しいエンドポイントは `api/` 以下に追加
- 新しいジョブ処理は `worker/` 以下に追加

## Key Constraints
- YouTube API quota: 無料枠 10,000/日。`search.list` は 100 quota/回
- OpenAI: `gpt-4o-mini` を使用。バッチ5件で呼び出す
- Discord Webhook: 1メッセージ 2000文字制限
- Supabase: `UNIQUE(platform, platform_id)` 制約に注意した upsert

## Current Status
`.agents/progress.md` を参照

## Reference
- 詳細仕様: `docs/spec/scout_system_spec.md`
- フェーズタスク: `.agents/phases/`
- 技術パターン: `.agents/skills/`
