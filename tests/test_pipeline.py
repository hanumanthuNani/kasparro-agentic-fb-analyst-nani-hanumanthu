from src.orchestrator.pipeline import run_pipeline

def test_pipeline_runs():
    result = run_pipeline("Analyze ROAS drop", return_output=True)
    assert "summary" in result
    assert "hypotheses" in result
    assert "validated" in result
    assert "creatives" in result
