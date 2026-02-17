# Phase 1: Foundation

## 目的
設定管理・DB初期化・基本クエリを整備し、SCOUT SYSTEM の最小実行基盤を作る。

## 完了条件（Definition of Done）
- `python -c "from db.queries import insert_run; print(insert_run('manual', {}))"` が例外なく `run_id` を返す
- `python -c "from db.queries import update_run_status; print('ok')"` が import エラーなく実行できる
- Supabase上で `scout_runs` テーブルの select が成功する

## タスクリスト
- [ ] 1. `.env.example` の作成
  - `SUPABASE_URL=`
  - `SUPABASE_KEY=`
  - `OPENAI_API_KEY=`
  - `OPENAI_MODEL=gpt-4o-mini`
  - `YOUTUBE_API_KEY=`
  - `DISCORD_WEBHOOK_URL=`
  - `HOT_THRESHOLD=85`
  - `BATCH_SIZE=5`

- [ ] 2. `config.py` の実装
  - `pydantic-settings` の `BaseSettings` を使う
  - 全環境変数を型付きフィールドで定義
  - `get_settings()` を用意して全体で共有

- [ ] 3. `supabase/migrations/001_init.sql` の作成
  - `scout_runs`
  - `scout_entities`
  - `scout_snapshots`
  - `scout_scores`
  - `scout_pins`
  - 仕様書 Section 3 の CREATE TABLE をすべて含める

- [ ] 4. `db/client.py` の実装
  - `config.py` から URL/KEY を読み取り Supabase client を初期化
  - シングルトンで管理

- [ ] 5. `db/queries.py` の基本形
  - `insert_run(run_type, config) -> run_id`
  - `update_run_status(run_id, status, summary=None) -> None`

- [ ] 6. 疎通テスト
  - `python -c "from db.queries import insert_run; print(insert_run('manual', {}))"`
  - run_id（UUID文字列）が返ること

## 参照ファイル
- `.agents/skills/supabase-crud.md`
- `docs/spec/scout_system_spec.md` Section 3（データ設計）

## 注意事項
- supabase クライアントは `db/client.py` 以外から import しない
- `.env` は `.gitignore` に追加する（`.env.example` は commit する）
