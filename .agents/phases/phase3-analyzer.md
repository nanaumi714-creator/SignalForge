# Phase 3: Analyzer

## 目的
`scout_snapshots` のデータを GPT に渡してスコアを算出し、`scout_scores` に保存する。

## 完了条件
- 17件の snapshot に対してスコアが算出され `scout_scores` に保存される
- スコアが Pydantic バリデーションを通過する

## タスクリスト
- [ ] 1. `models/schemas.py` への追加
  - `ScoreInput`
  - `ScoreOutput`
  - フィールド:
    - `demand_match` (0-30)
    - `improvement_potential` (0-20)
    - `ability_to_pay` (0-15)
    - `ease_of_contact` (0-15)
    - `style_fit` (0-20)
    - `summary`
    - `fit_reasons`
    - `recommended_offer`

- [ ] 2. `db/queries.py` への追加
  - `get_snapshots_by_run(run_id) -> list`
  - `insert_score(run_id, entity_id, score_data, gpt_model) -> score_id`
  - `get_last_score(entity_id) -> dict | None`

- [ ] 3. `worker/analyzer.py` の実装
  - `build_prompt(snapshot) -> str`
  - `call_gpt(prompt) -> ScoreOutput`
  - `calc_score_delta(entity_id, current_score) -> int`
  - `analyze_batch(run_id, snapshots) -> list[str]`
  - 5件ずつバッチ処理、例外時はスキップしてログ出力

## GPT プロンプト要件
- system: 仕様書 Section 6.5 の `SYSTEM_PROMPT` を使用
- user: `display_name / category / subscribers / total_views / upload_freq_days / recent_videos_json`
- `response_format={"type": "json_object"}` を指定
- JSONパース失敗時は retry 1回、再失敗時は当該エンティティをスキップ

## 参照ファイル
- `.agents/skills/openai-structured.md`
- `.agents/skills/supabase-crud.md`
- `docs/spec/scout_system_spec.md` Section 6（スコアリング設計）
