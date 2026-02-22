# Deployment Guide

SignalForge SCOUT SYSTEM のデプロイ手順書です。

## 1. 環境変数の設定

以下の環境変数をデプロイ先のサービス（Paas や Docker）に設定してください。

| 変数名 | 説明 | 設定値の例 / 取得先 |
|---|---|---|
| `SUPABASE_URL` | Supabase Cloud のプロジェクトURL | `https://xyz.supabase.co` (Settings > API) |
| `SUPABASE_KEY` | Supabase の ANON KEY | (Settings > API > anon public) |
| `OPENAI_API_KEY` | OpenAI の API キー | (Secret) |
| `YOUTUBE_API_KEY` | Google Cloud の YouTube Data API キー | (Secret) |
| `DISCORD_WEBHOOK_URL` | 通知先の Discord Webhook URL | `https://discord.com/api/webhooks/...` |
| `SCOUT_API_KEY` | API 呼び出し用のシークレットキー | 任意の強力な文字列 (Render の Env Vars で設定) |

## 2. Render へのデプロイ手順

Render では Docker を使用してデプロイします。

### 手順
1. Render Dashboard で `New + > Web Service` を選択。
2. リポジトリを接続。
3. **Runtime** に `Docker` を選択。
4. **Environment Variables** に上記の「1. 環境変数の設定」の各値を入力。
5. デプロイを開始。

### Docker でのローカル確認
本番環境に上げる前に、ローカルで Docker が動くか確認する場合は以下を実行します。
```bash
docker build -t signalforge-scout .
docker run -d -p 8000:8000 --env-file .env signalforge-scout
```

## 3. GitHub Actions による定時実行

1. GitHub リポジトリの `Settings > Secrets and variables > Actions` に以下を登録します。
   - `API_BASE_URL`: デプロイされた API のベースURL（例: `https://api.yourdomain.com`）
   - `SCOUT_API_KEY`: API 認証用のキー
2. `.github/workflows/scout-weekly.yml` が毎週月曜午前9時（JST）に自動実行されます。その際、ヘッダーにこのキーが追加されます。

## 4. 動作確認

### ヘルスチェック
`GET /` へのアクセスで `{"status":"online"}` が返ることを確認してください。

### API 実行テスト (PowerShell)
`.env` に設定した `SCOUT_API_KEY` を使用して、以下のコマンドで実行テストが可能です。

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-API-KEY" = "your_api_key_here"
}
$body = '{"run_type":"manual", "notify_discord":false}'

Invoke-RestMethod -Uri "http://localhost:8000/v1/scout/runs" -Method Post -Headers $headers -Body $body
```

## 5. 運用・保守

- **ログの確認**: コンテナの標準出力を確認してください (`docker logs -f <container_id>`)。
- **ヘルスチェック**: `GET /` は認証なしでアクセス可能です。