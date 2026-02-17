# Phase 6: Hybrid 60

## 目的
Tracked30 / New30 のハイブリッド60件をフル実装し、トレンド抽出を含む市場調査エンジンとして完成させる。

## 完了条件
- 1 run で60件が処理される
- Top10 / Hot10 / Watchlist が正しく生成される
- トレンドキーワードが 7d / 30d で抽出される

## タスクリスト
- [ ] 1. Tracked30 構成（`orchestrator.py`）
  - `get_tracked_entities(run_id) -> list[str]`
  - 内訳: 前回Top10 + 前回Hot8 + Watch上位7 + ManualPin5
  - 前回runがない場合は ManualPin 中心で構成

- [ ] 2. New30 発掘（`collector.py`）
  - `collect_seed(keywords, n=12) -> list[str]`
  - `collect_from_trends(trend_keywords, n=10) -> list[str]`
  - `collect_random(categories, n=8) -> list[str]`
  - Tracked30 と entity_id ベースで重複排除
  - 欠損分は random 枠で補充

- [ ] 3. トレンド抽出（`analyzer.py`）
  - `extract_trends(run_id) -> list[TrendObject]`
  - 7日/30日の snapshot 集計
  - GPTでキーワード抽出
  - Pythonで `growth_rate` 算出
  - 次runの `collect_from_trends` に渡す

- [ ] 4. `db/queries.py` への追加
  - `get_prev_run_classifications(classification) -> list[str]`
  - `get_watch_entities(limit=7) -> list[str]`
  - `get_pinned_entities() -> list[str]`

## 60件構成の詳細
- 仕様書 Section 4.2 の枠数と選出ロジックを厳密に実装する

## 参照ファイル
- `.agents/skills/youtube-api.md`
- `.agents/skills/openai-structured.md`
- `docs/spec/scout_system_spec.md` Section 4.2 / Section 7
