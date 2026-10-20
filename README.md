# Multi-Agent Trust Defense

A lightweight LangGraph-based multi-agent news analysis workflow that fetches news articles, routes them into specialized researcher agents, validates the outputs, scores trust, and produces a final report.

## Overview

This project is designed to simulate a fact-checking / trust-defense pipeline in which multiple agents analyze the same news evidence from different angles:

- Researcher A focuses on relevance
- Researcher B focuses on recency
- Validation checks whether each agent used its evidence appropriately
- Security monitoring converts validation results into trust scores
- Reporting synthesizes the final result into a user-facing summary

The project uses:

- GNews for external article retrieval
- Google Gemini for LLM-based reasoning
- LangGraph for orchestration
- Python + dotenv for environment configuration

## Project structure

```text
multi-agent-trust-defense/
├── app/
│   ├── agents/
│   │   ├── leader.py
│   │   ├── retrieval.py
│   │   ├── researcher_a.py
│   │   ├── researcher_b.py
│   │   ├── validation.py
│   │   ├── security_monitor.py
│   │   └── reporting.py
│   ├── graph/
│   │   └── workflow.py
│   ├── models/
│   │   └── state.py
│   ├── utils/
│   │   ├── gemini.py
│   │   └── news_api.py
│   └── main.py
├── .env
├── requirements.txt
├── README.md
└── cache/
```

## Workflow

The graph is built in `app/graph/workflow.py` and follows this sequence:

```text
START -> leader -> retrieval -> researcher_a -> validation -> security_monitor -> reporting -> END
                   \-> researcher_b -> validation
```

The key idea is:

- retrieval fetches article data
- relevance and recency analyses happen in parallel from different views of the same article set
- validation checks each researcher
- reporting presents the combined output

## Required environment variables

Create a `.env` file in the project root:

```env
GNEWS_API_KEY=your_gnews_api_key
GOOGLE_AI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_primary_model
GEMINI_FALLBACK_MODEL=your_fallback_model
SIMULATE_MALICIOUS_AGENTS=false
```

Notes:

- `GNEWS_API_KEY` is used by `app/utils/news_api.py`
- `GOOGLE_AI_API_KEY` is used by Gemini-based agents
- `GEMINI_MODEL` is optional but useful if you want to override the model explicitly
- `GEMINI_FALLBACK_MODEL` is used after a rate-limit response when configured
- `SIMULATE_MALICIOUS_AGENTS` defaults to `false`. Set it to `true` only when
  testing the trust and replacement workflow.

## Install dependencies

From the project root:

```powershell
cd "E:\main proj\multi-agent-trust-defense"
python -m venv .venv
.
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

```powershell
cd "E:\main proj\multi-agent-trust-defense"
.
.venv\Scripts\Activate.ps1
python -m app.main
```

Then enter a query when prompted, for example:

```text
Fuel prices
```

## What each agent does

### Leader

The leader agent logs the incoming user query and passes the state forward.

### Retrieval

The retrieval agent calls the news API and stores the fetched articles under:

```python
state["retrieved_information"] = {
    "relevance": [...],
    "recency": [...]
}
```

The same article set is used for both views, but the recency view is sorted by the newest `publishedAt` timestamps.

### Researcher A

Researcher A analyzes the relevance-oriented article set and produces a relevance-focused reasoning result.

### Researcher B

Researcher B analyzes the recency-oriented article set and produces a recency-focused reasoning result.

### Validation

Validation evaluates whether each researcher remained consistent with its assigned task using its own evidence.

The returned state looks like:

```python
{
    "validation_result": {
        "researcher_a": "CONSISTENT" or "INCONSISTENT",
        "researcher_b": "CONSISTENT" or "INCONSISTENT"
    }
}
```

### Security Monitor

The security monitor converts validation outcomes into trust-style statuses and stores them in:

```python
state["security_status"]
```

### Reporting

The reporting agent builds a final summary, combining:

- user query
- retrieved article lists
- researcher analysis outputs
- validation results
- security status

It then returns the final text in:

```python
state["final_report"]
```

## State schema

The workflow state is defined in `app/models/state.py`:

```python
from typing import TypedDict, List, Dict


class AgentState(TypedDict):
    user_query: str
    retrieved_information: Dict[str, List[Dict]]
    researcher_a_output: str
    researcher_b_output: str
    validation_result: Dict
    security_status: Dict
    final_report: str
```

## Notes on current implementation

This project is a working prototype rather than a production-ready application. Current characteristics include:

- the same article list may be reused for both relevance and recency views unless the API request is explicitly split by sort strategy
- strict environment-variable consistency is required (`GNEWS_API_KEY` vs. other names used in different files)
- validation and reporting depend on the expected state structure being present at runtime
- GNews can return rate-limit or authentication errors if the API key is missing, invalid, or overused

## Example runtime behavior

When running the app, you may see terminal output similar to:

```text
[LEADER] Received query:
Fuel prices
[RETRIEVAL] Fetching news...
[RESEARCHER A] Analyzing relevance...
[RESEARCHER B] Analyzing recency...
[VALIDATION] Checking researcher outputs...
[SECURITY MONITOR] Evaluating researcher trust...
[REPORTING] Generating final report...

==============================
FINAL REPORT
==============================
```

## Troubleshooting

### Missing API key

If GNews returns:

```text
GNews API error: 400 - {"errors":["You did not provide an API key."]}
```

then the key variable name being read by `news_api.py` does not match the key present in `.env`.

### Blank final report

If the report is blank, the usual cause is a mismatch between:

- the shape of the initial state in `app/main.py`
- the expected state defined in `app/models/state.py`

The state must include keys such as:

- `retrieved_information`
- `researcher_a_output`
- `researcher_b_output`
- `validation_result`
- `security_status`
- `final_report`

## Current status

The project is a working multi-agent prototype for news analysis and trust validation. It is useful for learning how a LangGraph workflow can organize specialized agents, but it still needs cleanup and standardization before it can be treated as a polished production system.
