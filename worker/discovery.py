"""Discovery worker for finding new channels via Web Search."""

import json
import logging
from typing import Any
from openai import OpenAI
from config import get_settings
from worker.search_tool import TavilySearchTool

logger = logging.getLogger(__name__)

DISCOVERY_SYSTEM_PROMPT = """
あなたは海外クリエイターの市場調査スペシャリストです。
提供されたWEB検索結果から、有望なYouTubeチャンネル名やYouTubeのハンドル名（@handle）を抽出してください。
出力は必ず以下のJSON形式で行ってください。

{
  "discovered_channels": [
    {
      "name": "チャンネル名またはクリエイター名",
      "handle": "@handle (分かれば)",
      "justification": "なぜ有望と考えたか（日本語1文）"
    }
  ]
}
""".strip()

class DiscoveryWorker:
    """Worker to discover new YouTube channels using OpenAI's native Web Search."""

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_search_model

    def discover(self, keywords: list[str]) -> list[dict[str, Any]]:
        """Main discovery flow using OpenAI's search-enabled model."""
        prompt = (
            f"以下のキーワードに関連する、最近話題の海外YouTubeチャンネルをWEB検索で見つけてください: {', '.join(keywords)}\n"
            "抽出したチャンネル名やハンドル名（@handle）をリストアップし、なぜ有望かの理由を日本語で添えてください。"
        )

        try:
            # Note: We use the specialized search model which has web search built-in.
            # Depending on the specific OpenAI API version, this might also be implemented 
            # as a tool: tools=[{"type": "web_search"}]
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": DISCOVERY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                # tools=[{"type": "web_search"}] # For standard models with tool support
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            all_discovered = data.get("discovered_channels", [])
            
            # Deduplication
            unique_results = []
            seen = set()
            for item in all_discovered:
                key = item.get("handle") or item.get("name")
                if key and key not in seen:
                    unique_results.append(item)
                    seen.add(key)
            return unique_results

        except Exception as e:
            logger.error(f"Discovery via OpenAI search failed: {e}")
            return []
