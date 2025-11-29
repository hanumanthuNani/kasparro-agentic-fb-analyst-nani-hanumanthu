from src.agents.llm_agent import LLMAgent
import json


class PlannerAgent:
    """
    Planner Agent:
    Converts user query into a structured plan that will be used
    by DataAgent, InsightAgent, EvaluatorAgent, and CreativeGenerator.
    """

    def __init__(self, llm_enabled=False):
        self.llm_enabled = llm_enabled
        if llm_enabled:
            self.llm = LLMAgent()

    def run(self, query: str, dataset_summary=None) -> dict:
        """
        Entry point. If LLM is enabled → use LLM planner
        Otherwise → manual planner.
        """
        if self.llm_enabled:
            return self.run_llm(query, dataset_summary)

        return self.run_manual(query)

    def run_manual(self, query: str) -> dict:
        """
        Manual deterministic planner.
        """

        if "7" in query or "week" in query:
            time_window = "last_7_days"
        else:
            time_window = "auto_detect"

        plan = {
            "query": query,
            "time_window": time_window,
            "steps": [
                "load_data",
                "summarize_data",
                "compute_trends",
                "detect_anomalies",
                "generate_hypotheses",
                "evaluate_hypotheses",
                "recommend_creatives"
            ],
            "metrics_of_interest": ["roas", "ctr", "spend", "impressions"]
        }

        return plan

    def run_llm(self, query: str, dataset_summary=None) -> dict:
        """
        LLM-powered planner using prompts/planner_prompt.md.
        """

        # Load prompt
        with open("prompts/planner_prompt.md", "r") as f:
            system_prompt = f.read()

        # Build user prompt
        user_prompt = (
            f"User query: {query}\n\n"
            f"Dataset summary:\n{json.dumps(dataset_summary, indent=2)}"
        )

        json_schema = {
            "query": "string",
            "time_window": "string",
            "steps": [],
            "metrics_of_interest": []
        }

        # Call LLM
        response = self.llm.structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_schema=json_schema
        )

        # Convert LLM output into dictionary
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Planner LLM returned invalid JSON: {response}")
