from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from .service import TikTokCopyService


app = FastAPI(title="TikTok Local Copy Generator", version="1.0.0")


class GenerateResponse(BaseModel):
    transcript: str
    generated: dict


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    country: str = Form(..., description="目标国家，例如 Indonesia"),
    brand_context: str | None = Form(default=None, description="品牌/产品补充说明"),
    video: UploadFile = File(..., description="用于分析的视频文件"),
) -> GenerateResponse:
    suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"

    try:
        service = TikTokCopyService()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            content = await video.read()
            temp.write(content)
            temp_path = Path(temp.name)

        transcript = service.transcribe_video(temp_path)
        generated = service.generate_copy(
            transcript=transcript,
            country=country,
            brand_context=brand_context,
        )
        return GenerateResponse(transcript=transcript, generated=generated)
    except Exception as exc:  # pragma: no cover - API layer fallback
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        try:
            temp_path.unlink(missing_ok=True)  # type: ignore[name-defined]
        except Exception:
            pass
