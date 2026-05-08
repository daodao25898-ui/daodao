from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .prompts import build_country_prompt
from .schemas import GeneratedCopy


class TikTokCopyService:
    def __init__(self, model: str = "gpt-4o-mini", allow_mock: bool = True) -> None:
        self.model = model
        self.mock_enabled = allow_mock and os.getenv("USE_MOCK_AI", "false").lower() == "true"

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key and not self.mock_enabled:
            raise RuntimeError(
                "缺少 OPENAI_API_KEY。请先设置环境变量，或设置 USE_MOCK_AI=true 进入可演示模式。"
            )

        self.client: Any = None
        if api_key:
            try:
                from openai import OpenAI
            except Exception as exc:
                raise RuntimeError(
                    "未安装 openai 依赖。请先执行: pip install -r requirements.txt"
                ) from exc
            self.client = OpenAI(api_key=api_key)

    def transcribe_video(self, video_path: Path) -> str:
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        if self.mock_enabled:
            return "[mock transcript] 这是一个展示商品使用前后效果的短视频，包含开箱、演示和用户反馈。"

        if self.client is None:
            raise RuntimeError("OpenAI client 未初始化")

        with video_path.open("rb") as f:
            transcription = self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
            )
        return transcription.text

    def _load_json_text(self, text: str) -> dict:
        payload = text.strip()
        if payload.startswith("```"):
            payload = payload.strip("`")
            payload = payload.replace("json\n", "", 1).strip()
        return json.loads(payload)

    def _mock_copy(self, country: str) -> GeneratedCopy:
        return GeneratedCopy(
            market_language="en",
            hooks=[
                f"POV: You found this in {country} and didn't expect THIS 😳",
                "Wait till the end for the real result 👀",
                "This is why everyone is talking about it today 🔥",
            ],
            caption_options=[
                "真实测了一周，效果比我预期更稳。想看完整过程我放在评论区，记得先收藏！✨",
                "今天用最简单的方式给你看重点：上手快、反馈直观、日常可复用。你会怎么用它？💬",
                "如果你也在找更省心的方案，这条一定要看完。细节和注意点都帮你整理好了 ✅",
            ],
            hashtag_sets=[
                ["#tiktokmademebuyit", "#fyp", "#viral", "#review", "#musthave", "#trending"],
                ["#dailyuse", "#beforeafter", "#tips", "#shopnow", "#creator", "#content"],
                ["#recommended", "#lifestyle", "#productdemo", "#honestreview", "#ugc", "#explore"],
            ],
            cta_options=[
                "想要同款清单，评论区打“1”我发你。",
                "还想看哪个国家版本？留言我继续做。",
                "点进主页看完整合集，下一条更详细。",
            ],
            compliance_notes="示例为演示模式输出，正式投放前请人工核验卖点真实性与当地合规要求。",
        )

    def generate_copy(
        self,
        transcript: str,
        country: str,
        brand_context: str | None = None,
    ) -> GeneratedCopy:
        if self.mock_enabled:
            return self._mock_copy(country)

        if self.client is None:
            raise RuntimeError("OpenAI client 未初始化")

        prompt = build_country_prompt(country=country, transcript=transcript, brand_context=brand_context)

        completion = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "你输出的内容必须是合法 JSON，且不要附加 markdown。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        parsed = self._load_json_text(completion.output_text)
        return GeneratedCopy.model_validate(parsed)
