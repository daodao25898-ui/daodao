from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from .schemas import GenerateRequestFromTranscript, GenerateResponse
from .service import TikTokCopyService


MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024
ALLOWED_SUFFIXES = {".mp4", ".mov", ".m4v", ".avi", ".webm", ".mpeg", ".mpg"}

app = FastAPI(title="TikTok Local Copy Generator", version="1.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    country: str = Form(..., min_length=2, max_length=50, description="目标国家，例如 Indonesia"),
    brand_context: str | None = Form(default=None, max_length=800, description="品牌/产品补充说明"),
    video: UploadFile = File(..., description="用于分析的视频文件"),
) -> GenerateResponse:
    suffix = Path(video.filename or "upload.mp4").suffix.lower() or ".mp4"
    temp_path: Path | None = None

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"不支持的视频格式: {suffix}")

    try:
        content = await video.read()
        if not content:
            raise HTTPException(status_code=400, detail="上传视频为空")
        if len(content) > MAX_VIDEO_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="视频过大，请上传 50MB 以内文件")

        service = TikTokCopyService()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            temp_path = Path(temp.name)

        transcript = service.transcribe_video(temp_path)
        generated = service.generate_copy(
            transcript=transcript,
            country=country,
            brand_context=brand_context,
        )
        return GenerateResponse(transcript=transcript, generated=generated)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - API layer fallback
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        try:
            if temp_path:
                temp_path.unlink(missing_ok=True)
        except Exception:
            pass


@app.post("/generate-from-transcript", response_model=GenerateResponse)
def generate_from_transcript(payload: GenerateRequestFromTranscript) -> GenerateResponse:
    try:
        service = TikTokCopyService()
        generated = service.generate_copy(
            transcript=payload.transcript,
            country=payload.country,
            brand_context=payload.brand_context,
        )
        return GenerateResponse(transcript=payload.transcript, generated=generated)
    except Exception as exc:  # pragma: no cover - API layer fallback
        raise HTTPException(status_code=400, detail=str(exc)) from exc
