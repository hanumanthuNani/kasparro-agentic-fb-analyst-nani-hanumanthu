# src/agents/insight_agent.py

import json
from typing import List, Dict
from src.agents.llm_agent import LLMAgent

class InsightAgent:
    """
    Generates hypotheses based on data summaries.
    This agent does NOT do the numeric math — that's EvaluatorAgent's job.
    """

    def __init__(self, llm_enabled: bool = False):
        self.llm_enabled = llm_enabled
        if llm_enabled:
            self.llm = LLMAgent()

    def run(self, summary: dict, plan: dict) -> List[Dict]:
        if self.llm_enabled:
            return self.run_llm(summary, plan)
        return self.run_manual(summary, plan)

    # ---------------------------------------------------------
    # MANUAL HYPOTHESIS GENERATION (rule-based)
    # ---------------------------------------------------------
    def run_manual(self, summary: dict, plan: dict) -> List[Dict]:
        hypotheses = []

        trends = summary.get("trends", {})
        roas_drop = trends.get("roas_last_7", 0) < trends.get("roas_prev_7", 999)
        ctr_drop = trends.get("ctr_last_7", 0) < trends.get("ctr_prev_7", 999)

        # H1: ROAS drop due to CTR decline
        if roas_drop and ctr_drop:
            hypotheses.append({
                "id": "H1",
                "description": "ROAS drop is likely caused by a decline in CTR for key campaigns.",
                "metrics_to_check": ["roas", "ctr"],
                "dimension": "campaign_name",
                "expected_pattern": "CTR last 7 < CTR previous 7, ROAS last 7 < ROAS previous 7"
            })

        # H2: Audience fatigue (impressions high but CTR low)
        hypotheses.append({
            "id": "H2",
            "description": "Possible audience fatigue: high impressions but CTR is below average.",
            "metrics_to_check": ["impressions", "ctr"],
            "dimension": "campaign_name",
            "expected_pattern": "High impressions combined with lower CTR"
        })

        # H3: Creative underperformance
        hypotheses.append({
            "id": "H3",
            "description": "Creative underperformance likely: some creative messages have below-average CTR.",
            "metrics_to_check": ["ctr", "creative_message"],
            "dimension": "creative_message",
            "expected_pattern": "Certain creative_message groups have low CTR"
        })

        # H4: Cost issues (if spend high but ROAS low)
        hypotheses.append({
            "id": "H4",
            "description": "Inefficient spending: campaigns with high spend but low ROAS.",
            "metrics_to_check": ["spend", "roas"],
            "dimension": "campaign_name",
            "expected_pattern": "Spend is high but ROAS is low"
        })

        # H5: Conversion issues (CTR ok but purchases low)
        hypotheses.append({
            "id": "H5",
            "description": "Conversion drop: CTR may be stable but purchases or revenue decreased.",
            "metrics_to_check": ["purchases", "ctr", "roas"],
            "dimension": "campaign_name",
            "expected_pattern": "CTR stable but purchases declined"
        })

        return hypotheses

    # ---------------------------------------------------------
    # LLM HYPOTHESIS GENERATION
    # ---------------------------------------------------------
    def run_llm(self, summary: dict, plan: dict) -> List[Dict]:
        """
        Use the prompts/insight_prompt.md (strict JSON) to request hypotheses.
        Returns list of hypotheses (dicts) or raises ValueError on bad JSON.
        """
        # load prompt file (this is the system prompt)
        with open("prompts/insight_prompt.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()

        # prepare a concise dataset summary for the LLM
        dataset_summary = {
            "rows": summary.get("rows"),
            "columns": summary.get("columns"),
            "trends": summary.get("trends", {}),
            "top_campaigns_by_spend": summary.get("top_campaigns_by_spend", []),
            "low_ctr_campaigns": summary.get("low_ctr_campaigns", []),
        }

        user_prompt = (
            f"Plan: {json.dumps(plan)}\n\n"
            f"Dataset summary: {json.dumps(dataset_summary, indent=2)}\n\n"
            "Produce 3-5 concise hypotheses with confidence and short evidence."
        )

        # JSON schema hint (keeps model focused)
        json_schema = {
            "hypotheses": [
                {
                    "id": "string",
                    "hypothesis": "string",
                    "confidence": "float",
                    "evidence": ["string"],
                    "recommended_tests": ["string"]
                }
            ]
        }

        # call LLM (structured JSON expected)
        raw = self.llm.structured(system_prompt=system_prompt, user_prompt=user_prompt, json_schema=json_schema)

        # clean & parse
        try:
            cleaned = raw.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Insight LLM returned invalid JSON. Raw output:\n{raw}\n\nError: {e}")

        # validate basic shape
        hypotheses = parsed.get("hypotheses", [])
        if not isinstance(hypotheses, list):
            raise ValueError("Insight LLM JSON does not contain 'hypotheses' list.")

        # normalize fields minimally (ensures consistency)
        normalized = []
        for i, h in enumerate(hypotheses):
            normalized.append({
                "id": h.get("id", f"H{i+1}"),
                "hypothesis": h.get("hypothesis") or h.get("description") or "",
                "confidence": float(h.get("confidence", 0.0)),
                "evidence": h.get("evidence", []),
                "recommended_tests": h.get("recommended_tests", [])
            })

        return normalized
