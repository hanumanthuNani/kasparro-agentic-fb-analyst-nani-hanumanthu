# src/agents/creative_generator.py

import json
from typing import List, Dict, Any
from pathlib import Path

from src.agents.llm_agent import LLMAgent

DEFAULT_PROMPT_PATH = "prompts/creative_prompt.md"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True, parents=True)


class CreativeGenerator:
    """
    Generates full creative packages using Gemini.
    """

    def __init__(self, llm_enabled: bool = False, model: str = "models/gemini-2.0-flash"):
        self.llm_enabled = llm_enabled
        self.model = model
        if self.llm_enabled:
            self.llm = LLMAgent(model=self.model)

    def run(self, validated_hypotheses: List[Dict[str, Any]],
            low_ctr_campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:

        if self.llm_enabled:
            return self.run_llm(validated_hypotheses, low_ctr_campaigns)
        return self.run_manual(validated_hypotheses, low_ctr_campaigns)

    # ---------------- Manual fallback -----------------
    def run_manual(self, validated_hypotheses, low_ctr_campaigns):
        recs = []
        for c in low_ctr_campaigns:
            recs.append({
                "campaign_name": c.get("campaign_name", "unknown"),
                "creative_type": "image",
                "new_headline": "Try Fresh Comfort Today",
                "new_message": "Highlight benefits and add a limited-time discount.",
                "new_cta": "Shop Now",
                "rationale": "Manual fallback suggestion."
            })

        out = {"recommendations": recs}
        (REPORTS_DIR / "creatives.json").write_text(json.dumps(out, indent=2))
        return out

    # ---------------- LLM Mode -----------------
    def run_llm(self, validated_hypotheses, low_ctr_campaigns):

        # Load prompt
        prompt_path = Path(DEFAULT_PROMPT_PATH)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Creative prompt not found at {prompt_path}")

        system_prompt = prompt_path.read_text()

        user_payload = {
            "validated_hypotheses": validated_hypotheses,
            "low_ctr_campaigns": low_ctr_campaigns,
            "instruction": "Generate a FULL creative package."
        }

        json_schema = {
            "recommendations": [
                {
                    "campaign_name": "string",
                    "creative_type": "string",
                    "new_headline": "string",
                    "new_message": "string",
                    "new_cta": "string",
                    "rationale": "string"
                }
            ]
        }

        # Call Gemini properly
        raw = self.llm.structured(
            system_prompt=system_prompt,
            user_prompt=json.dumps(user_payload, indent=2),
            json_schema=json_schema
        )

        # ---------------------------------------------------
        # CLEANING & JSON FIX
        # ---------------------------------------------------
        cleaned = raw.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "")

        try:
            parsed = json.loads(cleaned)
        except Exception:
            # emergency fallback to avoid crashing the pipeline
            parsed = {"recommendations_raw": cleaned}

        # Save result
        (REPORTS_DIR / "creatives.json").write_text(
            json.dumps(parsed, indent=2, ensure_ascii=False)
        )

        return parsed
