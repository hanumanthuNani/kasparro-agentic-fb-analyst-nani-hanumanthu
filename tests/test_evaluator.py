import pandas as pd
from src.agents.evaluator_agent import EvaluatorAgent

def test_evaluator_h1():
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "roas": [2.0, 1.0],
        "ctr": [0.02, 0.01],
        "spend": [100, 150],
        "impressions": [5000, 6000],
        "clicks": [100, 80],
        "purchases": [5, 4],
        "campaign_name": ["A", "A"]
    })

    ev = EvaluatorAgent({"confidence_min": 0.6})
    out = ev.evaluate(df, [{"id": "H1", "description": "roas drop"}])

    assert len(out) == 1
    assert out[0]["confidence"] >= 0.5
