from __future__ import annotations

from dataclasses import dataclass

from ..models import RetrievalResult


@dataclass(slots=True)
class FoundryPromptBundle:
    system_prompt: str
    user_prompt: str


def build_foundry_prompt(question: str, retrieved: list[RetrievalResult]) -> FoundryPromptBundle:
    """
    Helper for swapping the local deterministic answer composer with a Foundry-hosted model.
    """
    evidence = []
    for item in retrieved:
        evidence.append(f"[{item.chunk.doc_id}] ({item.chunk.doc_type}, {item.chunk.date}) {item.chunk.text}")

    system_prompt = (
        "You are a data operations copilot. Answer only from retrieved evidence, cite doc_ids, "
        "suggest likely root causes, and recommend next troubleshooting steps."
    )
    user_prompt = (
        f"Question: {question}\n\nRetrieved evidence:\n"
        + "\n".join(evidence)
        + "\n\nRespond with a concise answer, bullet root causes, bullet next steps, and citations."
    )
    return FoundryPromptBundle(system_prompt=system_prompt, user_prompt=user_prompt)
