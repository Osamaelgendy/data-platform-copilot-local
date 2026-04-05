from __future__ import annotations

import json
from pathlib import Path

from .models import DocumentChunk, SourceDocument


def load_corpus(corpus_dir: Path) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(corpus_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        documents.append(
            SourceDocument(
                doc_id=payload["doc_id"],
                title=payload["title"],
                doc_type=payload["doc_type"],
                content=payload["content"].strip(),
                date=payload["date"],
                tags=payload.get("tags", []),
                metadata=payload.get("metadata", {}),
            )
        )
    return documents


def chunk_documents(documents: list[SourceDocument], max_lines: int = 5) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        lines = [line.strip() for line in document.content.splitlines() if line.strip()]
        for index in range(0, len(lines), max_lines):
            part = lines[index:index + max_lines]
            chunk_id = f"{document.doc_id}::chunk-{index // max_lines + 1}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=document.doc_id,
                    title=document.title,
                    doc_type=document.doc_type,
                    text="\n".join(part),
                    date=document.date,
                    tags=document.tags,
                    metadata=document.metadata,
                )
            )
    return chunks
