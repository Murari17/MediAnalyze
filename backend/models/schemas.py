from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_length: int = Field(180, ge=60, le=400)


class SummarizeResponse(BaseModel):
    summary: str
    confidence: float
    explanation: str
    model: str


class AnonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class Redaction(BaseModel):
    label: str
    text: str
    token: str


class AnonymizeResponse(BaseModel):
    anonymized_text: str
    redactions: List[Redaction]
    entities_replaced: dict[str, str]
    spans: List[dict] | None = None
    confidence: float
    explanation: str
    ignored_terms: List[str] = []
    reason: str | None = None


class CompareRequest(BaseModel):
    text_a: str = Field(..., min_length=1)
    text_b: str = Field(..., min_length=1)
    threshold: float = Field(0.75, ge=0.0, le=1.0)
    max_sections: int = Field(6, ge=1, le=25)


class ChangedSection(BaseModel):
    side: str
    text: str
    best_match: str
    similarity: float


class CompareResponse(BaseModel):
    similarity_score: float
    diff_summary: str
    changed_sections: List[ChangedSection]
    confidence: float
    explanation: str
    model: str


class ValidateRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ValidateResponse(BaseModel):
    missing_fields: List[str]
    detected_fields: dict[str, object]
    low_confidence_fields: dict[str, object]
    inconsistencies: List[str]
    confidence: float
    explanation: str
    highlights: dict[str, str] | None = None


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ClassifyResponse(BaseModel):
    severity: str
    category: str
    confidence: float
    explanation: str
    top_keywords: List[str]


class ClassificationInput(BaseModel):
    category: str
    severity: str | None = None
    confidence: float | None = None


class ValidationInput(BaseModel):
    missing_fields: List[str]


class DecisionRequest(BaseModel):
    summary: str
    classification: ClassificationInput
    validation: ValidationInput


class DecisionResponse(BaseModel):
    decision: str
    reason: str
    confidence: float


class AnalyzeRequest(BaseModel):
    text_a: str = Field(..., min_length=1)
    text_b: Optional[str] = None


class AnalyzeResponse(BaseModel):
    summary: SummarizeResponse
    anonymized_text: AnonymizeResponse
    validation: ValidateResponse
    classification: ClassifyResponse
    comparison: Optional[CompareResponse]
    decision: DecisionResponse | None = None
    confidence: float
