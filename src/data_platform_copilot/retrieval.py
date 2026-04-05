from __future__ import annotations

import math
import re
from collections import Counter

from .models import DocumentChunk, RetrievalResult

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
STOPWORDS = {
    "a", "an", "and", "are", "after", "did", "for", "had", "in", "is", "it",
    "latest", "of", "on", "or", "the", "this", "to", "was", "what", "which",
    "why", "with", "week", "yesterday", "summarize",
}


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw_token in TOKEN_RE.findall(text.lower()):
        token = _normalize_token(raw_token.lower())
        if token and token not in STOPWORDS:
            tokens.append(token)
    return tokens


class SimpleRetriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self.doc_freq: Counter[str] = Counter()
        self.term_freqs: dict[str, Counter[str]] = {}

        for chunk in chunks:
            tokens = tokenize(self._chunk_text(chunk))
            counts = Counter(tokens)
            self.term_freqs[chunk.chunk_id] = counts
            for token in counts:
                self.doc_freq[token] += 1

    def search(self, question: str, limit: int = 5) -> list[RetrievalResult]:
        query_terms = tokenize(question)
        total_docs = max(len(self.chunks), 1)
        results: list[RetrievalResult] = []

        for chunk in self.chunks:
            counts = self.term_freqs[chunk.chunk_id]
            score = 0.0
            matched_terms: list[str] = []
            for term in query_terms:
                tf = counts.get(term, 0)
                if not tf:
                    continue
                idf = math.log((1 + total_docs) / (1 + self.doc_freq[term])) + 1
                score += tf * idf
                matched_terms.append(term)

            lower_question = question.lower()
            lower_text = self._chunk_text(chunk).lower()
            if "billing" in lower_question and "billing" in lower_text:
                score += 1.5
            if "quality" in lower_question and chunk.doc_type == "quality_report":
                score += 1.2
            if "deployment" in lower_question and chunk.doc_type == "deployment":
                score += 1.2
            if ("fail" in lower_question or "failed" in lower_question) and chunk.doc_type in {"incident", "run_log"}:
                score += 2.0
            if "row-count" in lower_question or "row count" in lower_question:
                if "row_count" in lower_text or "row count" in lower_text:
                    score += 1.2

            if score > 0:
                results.append(RetrievalResult(chunk=chunk, score=score, matched_terms=sorted(set(matched_terms))))

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    @staticmethod
    def _chunk_text(chunk: DocumentChunk) -> str:
        extras = " ".join(chunk.tags)
        metadata = " ".join(f"{key} {value}" for key, value in chunk.metadata.items())
        return f"{chunk.title}\n{chunk.text}\n{extras}\n{metadata}"


def _normalize_token(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("s") and len(token) > 4:
        return token[:-1]
    return token
