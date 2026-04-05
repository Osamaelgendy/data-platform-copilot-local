from __future__ import annotations

import json
from pathlib import Path

from .agent import DataPlatformCopilot
from .models import EvalCase, EvalScore


def load_eval_cases(path: Path) -> list[EvalCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvalCase(
            case_id=item["case_id"],
            question=item["question"],
            expected_terms=item["expected_terms"],
            expected_citations=item["expected_citations"],
            disallowed_terms=item.get("disallowed_terms", []),
        )
        for item in payload
    ]


def score_case(copilot: DataPlatformCopilot, case: EvalCase) -> EvalScore:
    answer = copilot.ask(case.question)
    full_text = " ".join([answer.answer, *answer.likely_root_causes, *answer.next_steps]).lower()

    term_hits = sum(1 for term in case.expected_terms if term.lower() in full_text)
    citation_hits = sum(1 for citation in case.expected_citations if citation in answer.citations)
    disallowed_hits = sum(1 for term in case.disallowed_terms if term.lower() in full_text)

    groundedness = round(min(1.0, len(answer.citations) / max(1, len(case.expected_citations))), 2)
    relevance = round(term_hits / max(1, len(case.expected_terms)), 2)
    citation_quality = round(citation_hits / max(1, len(case.expected_citations)), 2)
    hallucination_risk = round(min(1.0, disallowed_hits / max(1, len(case.disallowed_terms) or 1)), 2)

    notes = []
    if relevance < 0.75:
        notes.append("Answer missed some expected concepts.")
    if citation_quality < 1.0:
        notes.append("Answer did not cite all expected evidence.")
    if hallucination_risk > 0:
        notes.append("Answer included at least one disallowed concept.")
    if not notes:
        notes.append("Answer aligned well with expected evidence.")

    return EvalScore(
        case_id=case.case_id,
        groundedness=groundedness,
        relevance=relevance,
        citation_quality=citation_quality,
        hallucination_risk=hallucination_risk,
        notes=notes,
    )


def evaluate(corpus_dir: Path, eval_path: Path) -> str:
    copilot = DataPlatformCopilot(corpus_dir)
    cases = load_eval_cases(eval_path)
    scores = [score_case(copilot, case) for case in cases]

    lines = ["Evaluation results", "==================", ""]
    for score in scores:
        lines.append(f"{score.case_id}")
        lines.append(f"  groundedness: {score.groundedness:.2f}")
        lines.append(f"  relevance: {score.relevance:.2f}")
        lines.append(f"  citation_quality: {score.citation_quality:.2f}")
        lines.append(f"  hallucination_risk: {score.hallucination_risk:.2f}")
        lines.append(f"  notes: {'; '.join(score.notes)}")
        lines.append("")

    avg_groundedness = sum(item.groundedness for item in scores) / max(1, len(scores))
    avg_relevance = sum(item.relevance for item in scores) / max(1, len(scores))
    avg_citation = sum(item.citation_quality for item in scores) / max(1, len(scores))
    avg_hallucination = sum(item.hallucination_risk for item in scores) / max(1, len(scores))

    lines.append("Averages")
    lines.append(f"  groundedness: {avg_groundedness:.2f}")
    lines.append(f"  relevance: {avg_relevance:.2f}")
    lines.append(f"  citation_quality: {avg_citation:.2f}")
    lines.append(f"  hallucination_risk: {avg_hallucination:.2f}")
    return "\n".join(lines)
