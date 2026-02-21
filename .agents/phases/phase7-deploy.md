# Phase 7: Scheduled Runs & Deployment

## 目的
システムの定時自動実行設定（Weekly Run）を構築し、本番環境へのデプロイ準備（Docker / CI/CD）を完了させる。

## 完了条件
- GitHub Actions または Cron による定時実行ワークフローが定義されている
- アプリケーションをコンテナ化するための Dockerfile が作成されている
- 本番環境用の環境変数設定ガイドが整備されている

## タスクリスト
- [ ] 1. 定時実行ワークフローの構築
  - GitHub Actions `scout-weekly.yml` の作成
  - `/v1/scout/runs` エンドポイントを叩くスクリプトの用意
- [ ] 2. デプロイ準備（コンテナ化）
  - `Dockerfile` の作成
  - `docker-compose.yml` (ローカルテスト用) の整備
- [ ] 3. ドキュメント整備
  - `DEPLOY.md` の作成（デプロイ手順書）
  - 環境変数の本番設定ガイド
- [ ] 4. 検証
  - Docker 環境でのサーバー起動テスト
  - モック化された定時実行の疎通確認
