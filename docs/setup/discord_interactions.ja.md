# Discord Interactions 設定ガイド

このドキュメントでは、SignalForge の `POST /discord/interactions` を Discord スラッシュコマンドの受信口として使うための設定手順を説明します。

## 1. 前提

- SignalForge API が外部公開されていること（HTTPS 必須）。
- Discord Developer Portal で Application を作成済みであること。
- 環境変数を `.env` で設定できること。

## 2. Discord Developer Portal 側の設定

1. [Discord Developer Portal](https://discord.com/developers/applications) で対象 Application を開く。
2. **General Information** から以下を確認:
   - `Application ID`
   - `Public Key`
3. **Bot** を作成して、対象サーバーへ招待する。
4. **OAuth2 > URL Generator** で以下を有効化して招待 URL を発行:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: 必要最小限（例: `Send Messages`）
5. **Interactions Endpoint URL** に以下を設定:
   - `https://<your-domain>/discord/interactions`

> `Save Changes` 時に Discord から署名付き検証リクエスト（PING）が送られ、SignalForge 側が `{"type": 1}` を返せれば保存成功です。

## 3. SignalForge 側の環境変数

`config.py` で Discord 公開鍵を読むため、`.env` に `DISCORD_PUBLIC_KEY` を設定します。

```env
# 既存
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Interactions 用（Developer Portal の Public Key）
DISCORD_PUBLIC_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- `DISCORD_PUBLIC_KEY` は **Secret ではありません** が、設定値の取り違い防止のため `.env` 管理を推奨します。
- SignalForge は `X-Signature-Ed25519` / `X-Signature-Timestamp` を使って署名検証します。

## 4. Discord コマンド（推奨最小セット）

`/scout` ルートに以下サブコマンドを作成してください。

- `/scout run`  
  options:
  - `notify` (boolean)
  - `dry_run` (boolean)
  - `scope` (string: `daily` / `weekly` / `custom`)
- `/scout status`
- `/scout latest`
- `/scout health`

SignalForge 側実装はこの4つに対応しています。

## 5. ローカル確認手順

1. API 起動

```bash
uvicorn main:app --reload --port 8000
```

2. ngrok などで HTTPS 公開

```bash
ngrok http 8000
```

3. Developer Portal の Interactions Endpoint URL に ngrok URL を設定
   - 例: `https://xxxx-xx-xx-xx-xx.ngrok-free.app/discord/interactions`

4. Discord サーバーで `/scout health` を実行し、`SignalForge API is online` が返ることを確認

## 6. トラブルシュート

- `401 Missing Discord signature headers`
  - Discord 以外から直接叩いている可能性があります。
- `401 Invalid request signature`
  - `DISCORD_PUBLIC_KEY` の不一致を確認してください。
- `500 DISCORD_PUBLIC_KEY is not configured`
  - `.env` への設定漏れです。
- Endpoint URL 保存時に失敗する
  - 公開 URL が HTTPS ではない / SignalForge が起動していない / ルーティングが `/discord/interactions` ではない、を確認してください。

## 7. 関連 API

- Discord 入口: `POST /discord/interactions`
- 内部 API:
  - `GET /v1/scout/status`
  - `GET /v1/scout/reports/latest`
  - `POST /v1/scout/runs`

Discord 層は薄いルーターとして、上記内部 API / 既存処理を呼び出す構成です。
