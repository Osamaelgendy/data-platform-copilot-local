from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceDocument:
    doc_id: str
    title: str
    doc_type: str
    content: str
    date: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentChunk:
    chunk_id: str
    doc_id: str
    title: str
    doc_type: str
    text: str
    date: str
    tags: list[str]
    metadata: dict[str, Any]


@dataclass(slots=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float
    matched_terms: list[str]


@dataclass(slots=True)
class AgentAnswer:
    question: str
    answer: str
    likely_root_causes: list[str]
    next_steps: list[str]
    citations: list[str]
    retrieved: list[RetrievalResult]


@dataclass(slots=True)
class EvalCase:
    case_id: str
    question: str
    expected_terms: list[str]
    expected_citations: list[str]
    disallowed_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvalScore:
    case_id: str
    groundedness: float
    relevance: float
    citation_quality: float
    hallucination_risk: float
    notes: list[str]
