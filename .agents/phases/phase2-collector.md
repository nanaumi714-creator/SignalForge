# Phase 2: Collector

## 目的
YouTube API でクリエイター情報を収集し、`scout_snapshots` に保存できる状態にする。

## 完了条件
- seed キーワード `vtuber cover song` で3件以上取得できる
- 取得データが `scout_entities` と `scout_snapshots` に保存される

## タスクリスト
- [ ] 1. `db/queries.py` へ追加
  - `upsert_entity(platform, platform_id, display_name, ...) -> entity_id`
  - `insert_snapshot(run_id, entity_id, source_type, raw_data, ...) -> snapshot_id`

- [ ] 2. `worker/collector.py` の実装
  - `search_channels(keyword, max_results=12) -> list[str]`
  - `get_channel_details(channel_ids: list[str]) -> list[dict]`
  - `get_recent_videos(channel_id: str, n=10) -> list[dict]`
  - `calc_upload_freq(videos: list[dict]) -> float`
  - `collect_and_save(run_id, keywords, source_type) -> list[str]`

- [ ] 3. 手動テスト
  - `python -c` で `collect_and_save` を直接呼ぶ
  - snapshot_id が返ることを確認

## 参照ファイル
- `.agents/skills/youtube-api.md`
- `.agents/skills/supabase-crud.md`
- `docs/spec/scout_system_spec.md` Section 4（処理フロー）

## Quota 制約（必読）
- `search.list`: 100 quota / 回、1 run で5回以内を目安
- `channels.list`: 50件まで一括取得（1 quota / 回）
- Phase 2 では seed 12件 + pin 5件 = 17件を対象にする

## 戻り値の型
- 関数入出力は Pydantic モデルで定義し `models/schemas.py` に追加する
