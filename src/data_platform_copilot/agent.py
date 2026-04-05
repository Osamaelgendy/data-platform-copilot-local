from __future__ import annotations

from pathlib import Path

from .ingest import chunk_documents, load_corpus
from .models import AgentAnswer, RetrievalResult
from .retrieval import SimpleRetriever


class DataPlatformCopilot:
    def __init__(self, corpus_dir: Path) -> None:
        self.documents = load_corpus(corpus_dir)
        self.chunks = chunk_documents(self.documents)
        self.retriever = SimpleRetriever(self.chunks)

    def ask(self, question: str, limit: int = 5) -> AgentAnswer:
        retrieved = self.retriever.search(question, limit=limit)
        return self._compose_answer(question, retrieved)

    def show_index(self) -> str:
        lines = [f"Indexed documents: {len(self.documents)}", f"Indexed chunks: {len(self.chunks)}", ""]
        for document in self.documents:
            lines.append(f"- {document.doc_id} [{document.doc_type}] {document.title}")
        return "\n".join(lines)

    def _compose_answer(self, question: str, retrieved: list[RetrievalResult]) -> AgentAnswer:
        if not retrieved:
            return AgentAnswer(
                question=question,
                answer="I could not find supporting evidence in the indexed corpus.",
                likely_root_causes=["No relevant evidence was retrieved."],
                next_steps=["Ingest more run logs, incidents, or audit extracts for this domain."],
                citations=[],
                retrieved=[],
            )

        grouped_docs: list[str] = []
        evidence_lines: list[str] = []
        root_causes: list[str] = []
        next_steps: list[str] = []

        for result in retrieved:
            chunk = result.chunk
            if chunk.doc_id not in grouped_docs:
                grouped_docs.append(chunk.doc_id)
            sentence = self._first_sentence(chunk.text)
            if sentence and sentence not in evidence_lines:
                evidence_lines.append(sentence)

            root_causes.extend(self._root_causes_for_chunk(chunk))
            next_steps.extend(self._next_steps_for_chunk(chunk))

        return AgentAnswer(
            question=question,
            answer=self._answer_prefix(question, evidence_lines),
            likely_root_causes=_unique(root_causes)[:4],
            next_steps=_unique(next_steps)[:4],
            citations=grouped_docs[:5],
            retrieved=retrieved,
        )

    def _answer_prefix(self, question: str, evidence_lines: list[str]) -> str:
        lower_question = question.lower()
        if "latest data quality" in lower_question or "data quality issues" in lower_question:
            return "Recent data quality issues point to: " + " ".join(evidence_lines[:3])
        if "row-count mismatches" in lower_question or "row count mismatches" in lower_question:
            return "This week's row-count mismatches were reported in: " + " ".join(evidence_lines[:3])
        if "what changed" in lower_question and "deployment" in lower_question:
            return "The latest billing deployment introduced these operational changes: " + " ".join(evidence_lines[:3])
        if "why did yesterday" in lower_question or "pipeline fail" in lower_question:
            return "The most likely explanation for the failure is: " + " ".join(evidence_lines[:3])
        return "Based on the retrieved operational context: " + " ".join(evidence_lines[:3])

    @staticmethod
    def _first_sentence(text: str) -> str:
        first_line = text.splitlines()[0].strip()
        if first_line:
            return first_line if first_line.endswith(".") else first_line + "."
        sentence = text.split(".")[0].strip()
        return sentence + "." if sentence else ""

    @staticmethod
    def _root_causes_for_chunk(chunk) -> list[str]:
        text = chunk.text.lower()
        causes: list[str] = []
        if "schema" in text:
            causes.append("Schema or contract drift affected downstream expectations.")
        if "deployment" in text or chunk.doc_type == "deployment":
            causes.append("A recent deployment changed pipeline behavior.")
        if "row_count" in text or "row count" in text:
            causes.append("Audit checks detected row-count mismatches.")
        if "late-arriving" in text or "late arriving" in text:
            causes.append("Late-arriving records may have been dropped or delayed.")
        if "timeout" in text:
            causes.append("A timeout or dependency delay interrupted the pipeline.")
        if chunk.doc_type == "incident":
            causes.append("Incident evidence confirms an operational failure path.")
        return causes

    @staticmethod
    def _next_steps_for_chunk(chunk) -> list[str]:
        text = chunk.text.lower()
        steps: list[str] = []
        if "schema" in text:
            steps.append("Compare the latest data contract to the transform or load expectations.")
        if "billing_fact" in text:
            steps.append("Validate billing_fact row counts after replaying rejected records.")
        if "customer_dim" in text:
            steps.append("Rebuild customer_dim and rerun the dependent billing DAG.")
        if "deployment" in text:
            steps.append("Diff the deployed billing code against the previous release before retrying.")
        if "quality" in text or chunk.doc_type == "quality_report":
            steps.append("Review the affected quality checks and confirm whether the issue is isolated or systemic.")
        if "audit" in text or chunk.doc_type == "audit_extract":
            steps.append("Inspect audit extracts to confirm whether the mismatch persisted across multiple runs.")
        return steps


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
