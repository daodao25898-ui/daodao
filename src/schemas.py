from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedCopy(BaseModel):
    market_language: str = Field(..., min_length=2, description="target market language code")
    hooks: list[str] = Field(..., min_length=3, max_length=3)
    caption_options: list[str] = Field(..., min_length=3, max_length=3)
    hashtag_sets: list[list[str]] = Field(..., min_length=3, max_length=3)
    cta_options: list[str] = Field(..., min_length=3, max_length=3)
    compliance_notes: str


class GenerateRequestFromTranscript(BaseModel):
    country: str = Field(..., min_length=2, max_length=50)
    transcript: str = Field(..., min_length=5)
    brand_context: str | None = Field(default=None, max_length=800)


class GenerateResponse(BaseModel):
    transcript: str
    generated: GeneratedCopy
