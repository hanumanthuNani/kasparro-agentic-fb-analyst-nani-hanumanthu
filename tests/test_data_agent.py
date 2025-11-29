import pandas as pd
from src.agents.data_agent import DataAgent


def test_data_load_and_summary():
    config = {
        "use_sample_data": True,
        "data": {
            "sample_path": "data/sample_fb_ads.csv",
            "csv_env_var": "DATA_CSV"
        }
    }

    agent = DataAgent(config)
    df = agent.load_data()
    assert isinstance(df, pd.DataFrame)
    summary = agent.summarize_data(df, {})
    assert "overall" in summary
    assert "trends" in summary
