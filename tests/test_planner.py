from src.agents.planner_agent import PlannerAgent

def test_planner_llm():
    p = PlannerAgent(llm_enabled=False)
    plan = p.run("Analyze ROAS drop")
    assert "steps" in plan
    assert isinstance(plan["steps"], list)
