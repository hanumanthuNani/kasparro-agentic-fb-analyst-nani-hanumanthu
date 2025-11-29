# Kasparro Agentic Facebook Performance Analyst  
_Agentic Marketing Analytics System built by <Hanumanthu Nani>_

---

## 📌 Overview  
This project implements a **multi-agent autonomous system** that analyzes Facebook Ads data, diagnoses ROAS drops, identifies performance drivers, and generates new creative ideas using **Gemini 2.0 Flash**.

The system is fully modular, uses structured prompts, quantitative validation, and produces complete reports with insights + creatives.

This repo follows the **Kasparro assignment spec** exactly.

---

## 🚀 Features
- 🧠 **Planner Agent** — Converts user query → structured JSON plan  
- 📊 **Data Agent** — Loads CSV, cleans data, computes trends  
- 🔍 **Insight Agent (LLM)** — Generates hypotheses  
- 📈 **Evaluator Agent (Python)** — Validates hypotheses with numeric checks  
- 🎨 **Creative Generator (LLM)** — Produces full creative packages  
- 🧩 **LLM Agent** — Gemini interface with strict JSON outputs  
- 📂 **Reports** — report.md, insights.json, creatives.json  
- 🔐 Configurable using YAML  
- 🧪 Includes basic tests

---

## 🏗 Architecture Diagram

```

USER QUERY
↓
Planner Agent (LLM)
↓
Data Agent → Summary
↓
Insight Agent (LLM)
↓
Evaluator Agent (Python)
↓
Creative Generator (LLM)
↓
Final Report (Markdown + JSON)

```

---

## 📦 Repository Structure

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
│   ├── test_evaluator.py
│   └── test_data_agent.py
├── requirements.txt
├── Makefile OR run.sh
└── README.md

````

---

## ⚙️ Installation

### 1. Create environment
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
````

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Export Gemini API key

```bash
export GOOGLE_API_KEY="your-key"
```

Windows PowerShell:

```powershell
setx GOOGLE_API_KEY "your-key"
```

---

## ▶️ Running the Pipeline

#### CLI Command:

```bash
python -m src.run "Analyze ROAS drop"
```

Expected output:

* `reports/report.md`
* `reports/insights.json`
* `reports/creatives.json`

---

## 🧪 Tests

Run tests with:

```bash
pytest
```

Example:

* `test_evaluator.py`
* `test_data_agent.py`

---

## 🧠 How It Works (Short Explanation)

### 1. Planner Agent

Uses Gemini to break the query into subtasks:

```json
{
  "steps": ["load_data", "summarize_data", "compute_trends", ...]
}
```

### 2. Data Agent

Loads CSV → cleans → computes last-7 vs prev-7 trends.

### 3. Insight Agent

Generates structured hypotheses using LLM + prompt.

### 4. Evaluator Agent

Pure Python numeric validator. No hallucination risk.

### 5. Creative Generator

Uses Gemini to generate full creative packages.

---

## 📝 Example Output

(Stored in `reports/`)

**insights.json**
**creatives.json**
**report.md**

---

## 🏁 Reproducibility

* Gemini model seeded via config
* Consistent pipeline
* YAML for all thresholds
* Separate prompt files for evaluation consistency

---

## 🔖 Release

* Tag: `v1.0`
* PR: **self-review** summarizing design choices

---

## 🤝 Author

**<Hanumanthu Nani>**
Kasparro AI Assignment

