from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from .prompts import build_country_prompt


class TikTokCopyService:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("缺少 OPENAI_API_KEY，请先配置环境变量。")
        self.client = OpenAI(api_key=api_key)

    def transcribe_video(self, video_path: Path) -> str:
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        with video_path.open("rb") as f:
            transcription = self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
            )
        return transcription.text

    def generate_copy(
        self,
        transcript: str,
        country: str,
        brand_context: str | None = None,
    ) -> dict[str, Any]:
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

        text = completion.output_text.strip()
        return json.loads(text)
