# 進捗管理（AIセッション引き継ぎ）

## 現在のフェーズ
現在: **Phase 1 / 基盤構築（着手前）**

## 完了済みフェーズ
（なし）

## 現フェーズの進捗
- [ ] config.py（pydantic-settings で .env 読み込み）
- [ ] supabase/migrations/001_init.sql（5テーブル全定義）
- [ ] db/client.py（Supabase クライアント初期化）
- [ ] db/queries.py（insert_run / update_run_status 実装）
- [ ] 疎通確認（scout_runs テーブルへの select が通る）

## ブロッカー
- なし

## 次のセッション開始時の指示
AGENTS.md と `.agents/phases/phase1-foundation.md` を読んでから、`.env.example` 作成→`config.py` 実装→`db/client.py` 実装→`db/queries.py` 実装→疎通確認の順で作業を開始してください。

## 更新ルール（AIへの指示）
フェーズ完了時・セッション終了時に必ずこのファイルを更新すること。  
更新内容：完了タスクにチェック / 現在のフェーズ更新 / ブロッカー記録。
