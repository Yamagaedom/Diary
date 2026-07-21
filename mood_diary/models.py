"""Validated domain models (FR-001, FR-002, FR-003)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmotionAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    emotions: list[str] = Field(min_length=1, max_length=3)
    intensity: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=500)
    empathy: str = Field(min_length=1, max_length=1000)
    comfort: str = Field(min_length=1, max_length=1000)
    suggestion: str = Field(min_length=1, max_length=500)
    crisis: bool

    @field_validator("emotions")
    @classmethod
    def validate_emotions(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("감정 이름은 비어 있을 수 없습니다.")
        return cleaned


class DiaryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    created_at: datetime
    content: str = Field(min_length=1, max_length=5000)
    analysis: EmotionAnalysis

    @field_validator("content")
    @classmethod
    def reject_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("일기 내용을 입력해 주세요.")
        return value

