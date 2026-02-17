# Phase 4: Classifier & Notifier

## 目的
スコアを `top/hot/watch/normal` に分類し、Discord へ通知を送る。

## 完了条件
- Discordチャンネルに仕様書 Section 8.2 のフォーマットで通知が届く

## タスクリスト
- [ ] 1. `db/queries.py` への追加
  - `get_scores_by_run(run_id) -> list`
  - `update_score_classification(score_id, classification) -> None`

- [ ] 2. `worker/scorer.py` の実装
  - `classify_scores(scores: list) -> dict`
  - ルール:
    - `top`: total_score 上位10件
    - `hot`: total_score >= 85 かつ score_delta >= 5（top重複あり）
    - `watch`: top/hot 以外で total_score >= 60
    - `normal`: total_score < 60

- [ ] 3. `worker/notifier.py` の実装
  - `format_report(run_summary, top10, hot10, watchlist, trends) -> str`
  - `send_discord(message: str) -> None`
  - `httpx.post` で Webhook送信
  - 2000文字超は分割送信
  - top/hot 重複時は hot 側を `↑ Top参照`

## 通知フォーマット
- 仕様書 Section 8.2 をそのまま実装する
- セクション順: ヘッダー / TOP10 / HOT10 / WATCHLIST / TREND KEYWORDS

## 参照ファイル
- `.agents/skills/discord-webhook.md`
- `docs/spec/scout_system_spec.md` Section 6.2 / Section 8
