# Deployment Guide

SignalForge SCOUT SYSTEM のデプロイ手順書です。

## 1. 環境変数の設定

以下の環境変数をデプロイ先のサービス（Paas や Docker）に設定してください。

| 変数名 | 説明 | 例 |
|---|---|---|
| `SUPABASE_URL` | Supabase のプロジェクトURL | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Supabase の ANON または SERVICE_ROLE KEY | (Secret) |
| `OPENAI_API_KEY` | OpenAI の API キー | (Secret) |
| `YOUTUBE_API_KEY` | Google Cloud の YouTube Data API キー | (Secret) |
| `DISCORD_WEBHOOK_URL` | 通知先の Discord Webhook URL | `https://discord.com/api/webhooks/...` |
| `SCOUT_API_KEY` | API 呼び出し用のシークレットキー | (Secret) |

## 2. Docker での実行

### イメージのビルド
```bash
docker build -t signalforge-scout .
```

### コンテナの起動
```bash
docker run -d -p 8000:8000 --env-file .env signalforge-scout
```

## 3. GitHub Actions による定時実行

1. GitHub リポジトリの `Settings > Secrets and variables > Actions` に以下を登録します。
   - `API_BASE_URL`: デプロイされた API のベースURL（例: `https://api.yourdomain.com`）
   - `SCOUT_API_KEY`: API 認証用のキー
2. `.github/workflows/scout-weekly.yml` が毎週月曜午前9時（JST）に自動実行されます。その際、ヘッダーにこのキーが追加されます。

## 4. 運用・保守

- **ログの確認**: コンテナの標準出力を確認してください。
- **ヘルスチェック**: `GET /` へのアクセスで `{"status":"online"}` が返ることを確認してください。
