# Data Platform Copilot

Data teams lose time piecing together clues from pipeline runbooks, incident notes, audit tables, and data quality alerts. This repo shows how a local AI-style copilot can retrieve that operational context, answer troubleshooting questions with citations, and surface likely root causes plus next steps.

## Problem

When a pipeline breaks, analysts and engineers usually jump across Airflow logs, deployment notes, audit extracts, and incident tickets before they can even frame the issue. That slows down triage and makes operational knowledge hard to reuse.

## Solution

`Data Platform Copilot` is a practical local retrieval-augmented troubleshooting agent for data operations. It ingests runbooks, sample DAG documentation, incident reports, deployment changes, and data quality evidence, then answers natural-language questions such as:

- Why did yesterday's pipeline fail?
- Summarize the latest data quality issues.
- Which tables had row-count mismatches this week?
- What changed in the billing pipeline after the last deployment?

The implementation is intentionally local-first so it runs easily on one machine without cloud setup.

## Why It Matters

This project demonstrates the building blocks recruiters expect in production-style agent systems:

- grounded retrieval over mixed operational documents
- agent-style reasoning with citations
- root-cause and next-step recommendations
- evaluation for groundedness, relevance, citation quality, and hallucination risk

## Quickstart

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e . --no-build-isolation
data-platform-copilot ask "Why did yesterday's pipeline fail?"
data-platform-copilot evaluate
```

If your environment is offline and editable install tooling is unavailable, you can also run the demo directly:

```powershell
$env:PYTHONPATH="src"
py -3.11 -m data_platform_copilot.cli ask "Why did yesterday's pipeline fail?"
py -3.11 -m data_platform_copilot.cli evaluate
```

## Tech Stack

- Python 3.11
- Deterministic local retrieval and evaluation

## Repo Layout

```text
data-platform-copilot-local/
├── data/
│   ├── corpus/
│   └── eval/
├── src/data_platform_copilot/
│   ├── connectors/foundry.py
│   ├── agent.py
│   ├── cli.py
│   ├── evaluation.py
│   ├── ingest.py
│   ├── models.py
│   └── retrieval.py
└── tests/
```

## Evaluation

The evaluator scores:

- groundedness
- relevance
- citation_quality
- hallucination_risk

## Notes

- This version is intentionally local-only.
- It does not require Azure, Foundry, or any external service.
- The `foundry.py` helper remains as a prompt-shaping example, but it is not used at runtime in this local-only version.

## License

MIT
