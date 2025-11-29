# **Kasparro Agentic Facebook Performance Analyst**

*Agentic Marketing Analytics System by Hanumanthu Nani*

---

## **Overview**

This repository implements a multi-agent autonomous system designed to diagnose Facebook Ads performance, identify reasons for ROAS fluctuations, and generate improved creative recommendations.
The system follows the architecture required in the Kasparro assignment:
Planner → Data → Insight → Evaluator → Creative → Final Report.

The project incorporates structured prompts, modular agents, deterministic evaluation, and a reproducible pipeline.

---

## **Key Features**

* **Planner Agent**
  Converts a user query into a structured, step-wise analytic plan.

* **Data Agent**
  Loads the dataset, performs cleaning, summarizes performance, and computes trends.

* **Insight Agent (LLM)**
  Generates hypotheses grounded in the dataset summary.

* **Evaluator Agent (Python)**
  Validates each hypothesis using quantitative checks to prevent hallucination.

* **Creative Generator (LLM)**
  Generates improved creative directions for low-CTR campaigns using structured JSON.

* **LLM Agent**
  Unified interface for model communication with strict JSON enforcement.

* **Reports Output**
  Includes `report.md`, `insights.json`, and `creatives.json`.

* **Reproducible and Configurable**
  YAML-based configuration for paths, seeds, thresholds.

* **Automated Tests**
  Lightweight tests for DataAgent, EvaluatorAgent, PlannerAgent, and Pipeline.

---

## **Architecture**

```
User Query
      ↓
Planner Agent (LLM)
      ↓
Data Agent  →  Summary + Trends
      ↓
Insight Agent (LLM)
      ↓
Evaluator Agent (Python numeric checks)
      ↓
Creative Generator (LLM)
      ↓
Final Report (Markdown + JSON)
```

---

## **Repository Structure**

```
.
├── config/
│   └── config.yaml
├── data/
│   ├── sample_fb_ads.csv
│   ├── synthetic_fb_ads_undergarments.csv
│   └── README.md
├── prompts/
│   ├── planner_prompt.md
│   ├── insight_prompt.md
│   ├── evaluator_prompt.md
│   └── creative_prompt.md
├── reports/
│   ├── report.md
│   ├── insights.json
│   └── creatives.json
├── logs/
├── src/
│   ├── run.py
│   ├── orchestrator/
│   │   └── pipeline.py
│   ├── agents/
│   │   ├── llm_agent.py
│   │   ├── planner_agent.py
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── evaluator_agent.py
│   │   └── creative_generator.py
│   └── utils/
│       ├── config_loader.py
│       └── logging_utils.py
├── tests/
│   ├── test_data_agent.py
│   ├── test_evaluator.py
│   ├── test_planner.py
│   └── test_pipeline.py
├── requirements.txt
├── Makefile (or run.sh)
└── README.md
```

---

## **Installation**

### Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Set API key for the LLM

Windows:

```powershell
setx GOOGLE_API_KEY "your-key"
```

Linux/Mac:

```bash
export GOOGLE_API_KEY="your-key"
```

---

## **Running the Pipeline**

Run the full pipeline with:

```bash
python -m src.run "Analyze ROAS drop"
```

Outputs generated in `reports/`:

* `report.md`
* `insights.json`
* `creatives.json`

---

## **Tests**

Execute all tests:

```bash
pytest -q
```

Included tests:

* PlannerAgent
* DataAgent
* EvaluatorAgent
* Pipeline flow

All tests are minimal, fast, and focus on functional behavior.

---

## **Configuration**

All pipeline behavior is controlled via:

```
config/config.yaml
```

This includes:

* dataset paths
* environment variable for original CSV
* confidence thresholds
* seed values
* reports/logs output directories

---

## **Example Output**

Generated during pipeline execution:

* `insights.json` contains validated hypotheses
* `creatives.json` contains structured creative recommendations
* `report.md` composes everything into a readable summary

---

## **Reproducibility & Submission Requirements**

This project satisfies all Kasparro assignment requirements:

* Clear multi-agent architecture
* Planner → Insight → Evaluator → Creative loop
* Structured prompts separated into a `prompts/` directory
* Reproducible pipeline using deterministic evaluator
* Lightweight automated tests
* Version-locked requirements
* Release tagging and PR for self-review

---

## **Author**

**Hanumanthu Nani**
Kasparro Applied AI Engineer Assignment

---
