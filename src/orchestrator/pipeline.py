# import json
# from pathlib import Path
#
# from src.agents.planner_agent import PlannerAgent
# from src.agents.data_agent import DataAgent
# from src.agents.insight_agent import InsightAgent
# from src.agents.evaluator_agent import EvaluatorAgent
# from src.agents.creative_generator import CreativeGenerator
# from src.utils.config_loader import load_config
#
# REPORT_DIR = Path("reports")
# REPORT_DIR.mkdir(exist_ok=True, parents=True)
#
#
# def run_pipeline(query: str):
#     # ------------------------------------------------------------
#     # Load config
#     # ------------------------------------------------------------
#     cfg = load_config("config/config.yaml")
#     print("CONFIG =", cfg)
#
#     # ------------------------------------------------------------
#     # Instantiate agents (LLM-enabled where required)
#     # ------------------------------------------------------------
#     planner = PlannerAgent(llm_enabled=True)
#     data_agent = DataAgent(cfg)
#     insight_agent = InsightAgent(llm_enabled=True)   # Gemini version
#     evaluator = EvaluatorAgent(cfg)                  # Python-only evaluator
#     creative_gen = CreativeGenerator(llm_enabled=True, model="models/gemini-2.0-flash")
#
#     # ------------------------------------------------------------
#     # 1) PLAN
#     # ------------------------------------------------------------
#     summary_preview = {"rows": "unknown"}  # Will update later
#     plan = planner.run(query, dataset_summary=summary_preview)
#     print("[PIPELINE] Plan created.")
#
#     # ------------------------------------------------------------
#     # 2) LOAD DATA
#     # ------------------------------------------------------------
#     df = data_agent.load_data()
#     summary_preview["rows"] = len(df)
#
#     # ------------------------------------------------------------
#     # 3) SUMMARIZE + TRENDS
#     # ------------------------------------------------------------
#     summary = data_agent.summarize(df)
#     print("[PIPELINE] Summary generated.")
#
#     # ------------------------------------------------------------
#     # 4) GENERATE HYPOTHESES (LLM)
#     # ------------------------------------------------------------
#     hypotheses = insight_agent.run(summary, plan)
#     print("[PIPELINE] Hypotheses generated:", len(hypotheses))
#
#     # ------------------------------------------------------------
#     # 5) EVALUATE HYPOTHESES (Python)
#     # ------------------------------------------------------------
#     validated = evaluator.evaluate(df, [
#         {
#             "id": h["id"],
#             "description": h.get("hypothesis") or h.get("description", "")
#         } for h in hypotheses
#     ])
#     print("[PIPELINE] Hypotheses validated.")
#
#     (REPORT_DIR / "insights.json").write_text(
#         json.dumps(validated, indent=2, ensure_ascii=False)
#     )
#
#     # ------------------------------------------------------------
#     # 6) LOW CTR campaigns (input for creative agent)
#     # ------------------------------------------------------------
#     low_ctr_df = df[df["ctr"] < df["ctr"].mean()]
#     low_ctr_campaigns = low_ctr_df.groupby("campaign_name").agg(
#         ctr=("ctr", "mean"),
#         audience_type=("audience_type", "first"),
#         platform=("platform", "first")
#     ).reset_index().to_dict(orient="records")
#
#     # ------------------------------------------------------------
#     # 7) CREATIVE RECOMMENDATIONS (LLM)
#     # ------------------------------------------------------------
#     creatives = creative_gen.run(validated, low_ctr_campaigns)
#     print("[PIPELINE] Creative recommendations generated.")
#
#     # ------------------------------------------------------------
#     # 8) Generate Final Report
#     # ------------------------------------------------------------
#     md = []
#     md.append("# Automated Facebook Ads Performance Report\n")
#     md.append("## Query\n")
#     md.append(query + "\n")
#
#     md.append("## Hypotheses\n")
#     for h in validated:
#         md.append(f"### {h['id']}")
#         md.append(f"- Description: {h['description']}")
#         md.append(f"- Confidence: {h['confidence']}")
#         md.append(f"- Evidence: {h['evidence']}\n")
#
#     md.append("## Creative Recommendations\n")
#     md.append(json.dumps(creatives, indent=2, ensure_ascii=False))
#
#     (REPORT_DIR / "report.md").write_text("\n".join(md))
#
#     print("[PIPELINE] Report generated.")
#     print("[PIPELINE] Pipeline completed successfully.")
import json
from pathlib import Path

from src.agents.planner_agent import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_generator import CreativeGenerator
from src.utils.config_loader import load_config

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True, parents=True)


def run_pipeline(query: str, return_output: bool = False):
    """
    Main pipeline.
    If return_output=True → returns dict for pytest validation.
    Otherwise → behaves normally.
    """
    # ------------------------------------------------------------
    # Load config
    # ------------------------------------------------------------
    cfg = load_config("config/config.yaml")
    print("CONFIG =", cfg)

    # ------------------------------------------------------------
    # Instantiate agents (LLM-enabled where required)
    # ------------------------------------------------------------
    planner = PlannerAgent(llm_enabled=True)
    data_agent = DataAgent(cfg)
    insight_agent = InsightAgent(llm_enabled=True)   # Gemini version
    evaluator = EvaluatorAgent(cfg)                  # Python-only evaluator
    creative_gen = CreativeGenerator(llm_enabled=True, model="models/gemini-2.0-flash")

    # ------------------------------------------------------------
    # 1) PLAN
    # ------------------------------------------------------------
    summary_preview = {"rows": "unknown"}
    plan = planner.run(query, dataset_summary=summary_preview)
    print("[PIPELINE] Plan created.")

    # ------------------------------------------------------------
    # 2) LOAD DATA
    # ------------------------------------------------------------
    df = data_agent.load_data()
    summary_preview["rows"] = len(df)

    # ------------------------------------------------------------
    # 3) SUMMARY + TRENDS
    # ------------------------------------------------------------
    summary = data_agent.summarize_data(df, plan)
    print("[PIPELINE] Summary generated.")

    # ------------------------------------------------------------
    # 4) INSIGHT (LLM)
    # ------------------------------------------------------------
    hypotheses = insight_agent.run(summary, plan)
    print("[PIPELINE] Hypotheses generated:", len(hypotheses))

    # ------------------------------------------------------------
    # 5) EVALUATE (Python)
    # ------------------------------------------------------------
    validated = evaluator.evaluate(df, [
        {
            "id": h["id"],
            "description": h.get("hypothesis") or h.get("description", "")
        } for h in hypotheses
    ])
    print("[PIPELINE] Hypotheses validated.")

    (REPORT_DIR / "insights.json").write_text(
        json.dumps(validated, indent=2, ensure_ascii=False)
    )

    # ------------------------------------------------------------
    # 6) LOW CTR CAMPAIGNS
    # ------------------------------------------------------------
    low_ctr_df = df[df["ctr"] < df["ctr"].mean()]
    low_ctr_campaigns = low_ctr_df.groupby("campaign_name").agg(
        ctr=("ctr", "mean"),
        audience_type=("audience_type", "first"),
        platform=("platform", "first")
    ).reset_index().to_dict(orient="records")

    # ------------------------------------------------------------
    # 7) CREATIVE RECOMMENDATIONS
    # ------------------------------------------------------------
    creatives = creative_gen.run(validated, low_ctr_campaigns)
    print("[PIPELINE] Creative recommendations generated.")

    # ------------------------------------------------------------
    # 8) REPORT
    # ------------------------------------------------------------
    md = []
    md.append("# Automated Facebook Ads Performance Report\n")
    md.append("## Query\n")
    md.append(query + "\n")

    md.append("## Hypotheses\n")
    for h in validated:
        md.append(f"### {h['id']}")
        md.append(f"- Description: {h['description']}")
        md.append(f"- Confidence: {h['confidence']}")
        md.append(f"- Evidence: {h['evidence']}\n")

    md.append("## Creative Recommendations\n")
    md.append(json.dumps(creatives, indent=2, ensure_ascii=False))

    (REPORT_DIR / "report.md").write_text("\n".join(md))

    print("[PIPELINE] Report generated.")
    print("[PIPELINE] Pipeline completed successfully.")

    # ------------------------------------------------------------
    # RETURN OUTPUT FOR TESTS
    # ------------------------------------------------------------
    if return_output:
        return {
            "plan": plan,
            "summary": summary,
            "hypotheses": hypotheses,
            "validated": validated,
            "creatives": creatives
        }
