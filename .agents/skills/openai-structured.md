# OpenAI Structured Output パターン（SCOUT SYSTEM向け）

## 基本パターン: response_format で JSON 強制
```python
import json
from openai import OpenAI


def call_json(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(resp.choices[0].message.content)
```

## バッチ処理パターン（5件ずつ）
```python
import time


def batched(items: list, size: int = 5):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def process_in_batches(items: list, worker_fn):
    results = []
    for batch in batched(items, size=5):
        results.extend(worker_fn(batch))
        time.sleep(0.5)
    return results
```

## スコアリング用プロンプト
```python
SYSTEM_PROMPT = """
あなたは海外クリエイターのスカウト担当アナリストです。
与えられたYouTubeチャンネルデータを分析し、以下のJSON形式で返答してください。
必ずJSONのみを返し、説明文は不要です。

{
  "demand_match": <0-30の整数>,
  "improvement_potential": <0-20の整数>,
  "ability_to_pay": <0-15の整数>,
  "ease_of_contact": <0-15の整数>,
  "style_fit": <0-20の整数>,
  "summary": "<200字以内の日本語サマリ>",
  "fit_reasons": ["<理由1>", "<理由2>", "<理由3>"],
  "recommended_offer": "<推奨オファー内容1文>"
}
"""

USER_PROMPT_TEMPLATE = """
チャンネル名: {display_name}
カテゴリ: {category}
登録者数: {subscribers}
総再生数: {total_views}
平均投稿間隔: {upload_freq_days}日
直近動画:
{recent_videos_json}
"""
```

## Pydantic バリデーションパターン
```python
import json
from pydantic import ValidationError


def parse_score_output(raw_text: str, ScoreOutput):
    try:
        return ScoreOutput.model_validate(json.loads(raw_text))
    except (json.JSONDecodeError, ValidationError):
        # retry 1
        return None
```

- 1回目失敗: retry 1回
- 再失敗: 当該エンティティをスキップしてログ

## トレンド抽出用プロンプト
```python
TREND_SYSTEM_PROMPT = """
You are a trend analyst for creator markets.
Return JSON only.
Generate keyword clusters for 7d and 30d windows.
Allowed growth_signal values: burst, stable, emerging.
"""
```

- `growth_signal` 定義:
  - `burst`: 直近急伸
  - `stable`: 継続成長
  - `emerging`: 初期立ち上がり

## エラーハンドリング
- `JSONDecodeError`: retry 1回 → スキップ
- `ValidationError`: ログ出力 → スキップ
- `RateLimitError`: 10秒待機 → retry
- `APIError`: ログ出力 → スキップ

## コスト目安
- `gpt-4o-mini` を使用
- 1 run 想定: `60件 × 800 token = 48,000 token`
- 週4 run想定で低コスト運用（実運用時はOpenAI最新価格表で再計算）
