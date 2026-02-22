"""Analyzer worker for GPT-based scoring."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from config import get_settings
from db.queries import get_last_score, insert_score, get_scores_by_run
from models.schemas import ScoreInput, ScoreOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
あなたは海外クリエイターの市場分析スペシャリストです。
提供されたYouTubeチャンネルデータ（登録者数、再生数、直近の通常動画・ライブ・ショートの分布とタイトル）を詳細に分析し、以下のJSON形式で返答してください。
特に「どのような企画がヒットしているか（企画力）」「ライブやショートの活用戦略」を重点的に評価してください。

{
  "demand_match": <0-30の整数>,
  "improvement_potential": <0-20の整数>,
  "ability_to_pay": <0-15の整数>,
  "ease_of_contact": <0-15 de 整数>,
  "style_fit": <0-20の整数>,
  "summary": "<200字以内の日本語サバリ。動画形式の活用傾向を含めてください>",
  "fit_reasons": ["<企画ジャンルの評価>", "<動画形式の活用戦略>", "<成長ポテンシャル>"],
  "recommended_offer": "<具体的な推奨オファー提案1文>"
}
""".strip()


class Analyzer:
    """GPT scoring worker for snapshots."""

    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.batch_size = settings.batch_size
        self.client = OpenAI(api_key=settings.openai_api_key)

    def build_prompt(self, snapshot: ScoreInput) -> str:
        """Build user prompt from snapshot record."""

        return (
            f"チャンネル名: {snapshot.display_name}\n"
            f"カテゴリ: {snapshot.category or 'unknown'}\n"
            f"登録者数: {snapshot.subscribers}\n"
            f"総再生数: {snapshot.total_views}\n"
            f"平均投稿間隔: {snapshot.upload_freq_days}日\n"
            "直近動画:\n"
            f"{json.dumps(snapshot.recent_videos_json, ensure_ascii=False)}"
        )

    def call_gpt(self, prompt: str) -> ScoreOutput:
        """Call OpenAI and parse validated score output with bounded retry."""

        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                )
                content = response.choices[0].message.content or "{}"
                return ScoreOutput.model_validate(json.loads(content))
            except (json.JSONDecodeError, ValidationError):
                logger.exception("Invalid GPT output. attempt=%s", attempt + 1)
                if attempt == 0:
                    time.sleep(0.3)
                    continue
                raise

        raise ValueError("Unreachable GPT parse failure")

    def calc_score_delta(self, entity_id: str, current_score: int) -> int:
        """Calculate score difference from latest stored score."""

        previous = get_last_score(entity_id)
        if previous is None:
            return 0

        previous_total = int(float(previous.get("total_score", 0)))
        return current_score - previous_total

    def analyze_batch(self, run_id: str, snapshots: list[dict[str, Any]]) -> list[str]:
        """Analyze snapshots in batches and save score rows."""

        errors: list[str] = []

        for idx in range(0, len(snapshots), self.batch_size):
            batch = snapshots[idx : idx + self.batch_size]
            for raw in batch:
                entity_id = str(raw.get("entity_id", ""))
                try:
                    score_input = ScoreInput.model_validate(raw)
                    prompt = self.build_prompt(score_input)
                    score_output = self.call_gpt(prompt)
                    score_delta = self.calc_score_delta(entity_id, score_output.total_score)

                    payload = score_output.model_dump()
                    payload["score_delta"] = score_delta

                    insert_score(
                        run_id=run_id,
                        entity_id=entity_id,
                        score_data=payload,
                        gpt_model=self.model,
                    )
                    logger.info("Analyzer saved score. run_id=%s entity_id=%s", run_id, entity_id)
                except Exception as exc:
                    msg = f"Analyzer skipped entity_id={entity_id}: {exc}"
                    logger.exception(msg)
                    errors.append(msg)
            time.sleep(0.5)

        return errors

    def analyze_aggregated(self, run_id: str, snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze multiple entities at once and return top recommendations."""
        if not snapshots:
            return {"recommendations": []}

        # Context build for multiple entities
        context_items = []
        for s in snapshots[:10]: # Limit to 10 for context window
            context_items.append(
                f"ID: {s['entity_id']}, Name: {s['display_name']}, Subs: {s['subscribers']}, Views: {s['total_views']}"
            )
        
        prompt = "以下は収集されたチャンネルリストです:\n" + "\n".join(context_items)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_AGGREGATED},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            logger.exception("Aggregated analysis failed.")
            return {"recommendations": [], "error": "Analysis failed"}

    def extract_trends(self, run_id: str) -> dict[str, Any]:
        """
        Analyze recent scores to identify trends.
        """
        try:
            scores = get_scores_by_run(run_id)
            if not scores:
                return {"keywords": []}

            text_context = "\n".join([
                f"Entity: {s['display_name']}, TotalScore: {s['total_score']}, Delta: {s['score_delta']}"
                for s in scores[:20]
            ])

            prompt = (
                "以下の分析結果からトレンドワードを3つ抽出してください。\n"
                "返答形式: キーワード1, キーワード2, キーワード3\n\n"
                f"{text_context}"
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは市場アナリストです。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50
            )
            keywords_text = response.choices[0].message.content or ""
            keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
            
            return {
                "7d_trends": keywords[:2],
                "30d_trends": keywords[1:3],
                "keywords": keywords
            }
        except Exception:
            logger.exception("Trend extraction failed.")
            return {"errors": ["Trend extraction failed"]}


SYSTEM_PROMPT_AGGREGATED = """
あなたは海外クリエイターの市場アナリストです。
提供された複数のYouTubeチャンネルデータリストを分析し、スカウト優先度が高い上位3件を選んで以下のJSON形式で返答してください。
必ずJSONのみを返し、説明文は不要です。

{
  "recommendations": [
    {
      "rank": <1-3の整数>,
      "name": "<チャンネル名>",
      "id": "<entity_id>",
      "score_preview": <0-100の推定合計スコア>,
      "reason": "<日本語での選定理由1文>",
      "recommended_offer": "<具体的な推奨オファー1文>"
    }
  ]
}
""".strip()
