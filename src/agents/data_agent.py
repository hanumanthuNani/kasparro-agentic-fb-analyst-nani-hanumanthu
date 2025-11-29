import os
import pandas as pd


class DataAgent:
    """
    Loads Facebook Ads CSV and produces summaries
    needed by InsightAgent and EvaluatorAgent.
    """

    def __init__(self, config: dict):
        self.config = config

    # --------------------------
    # 1. Load Data
    # --------------------------
    def load_data(self) -> pd.DataFrame:
        use_sample = self.config.get("use_sample_data", True)

        if use_sample:
            csv_path = self.config["data"]["sample_path"]
        else:
            env_var = self.config["data"]["csv_env_var"]
            csv_path = os.getenv(env_var)
            if csv_path is None:
                raise RuntimeError(
                    f"Full dataset mode enabled but {env_var} is not set."
                )

        df = pd.read_csv(csv_path)
        df = self._clean(df)
        return df

    # --------------------------
    # 2. Clean Data
    # --------------------------
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare columns: date → datetime, numeric → floats."""

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        numeric_cols = ["spend", "impressions", "clicks", "ctr",
                        "purchases", "revenue", "roas"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    # --------------------------
    # 3. Pipeline-compatible name
    # --------------------------
    def summarize(self, df: pd.DataFrame, plan: dict = None) -> dict:
        """
        Compatibility wrapper for pipeline.
        Calls summarize_data() internally.
        """
        return self.summarize_data(df, plan)

    # --------------------------
    # 4. Summaries
    # --------------------------
    def summarize_data(self, df: pd.DataFrame, plan: dict) -> dict:
        """Returns summaries: overall metrics, by campaign, trends."""

        summary = {}

        summary["overall"] = {
            "avg_roas": df["roas"].mean(),
            "avg_ctr": df["ctr"].mean(),
            "total_spend": df["spend"].sum(),
        }

        summary["by_campaign"] = (
            df.groupby("campaign_name")[["roas", "ctr", "spend"]]
            .agg(["mean", "sum"])
            .reset_index()
            .to_dict(orient="records")
        )

        summary["trends"] = self._compute_trends(df)

        return summary

    # --------------------------
    # 5. Trend Calculation
    # --------------------------
    def _compute_trends(self, df: pd.DataFrame) -> dict:
        """Compute last 7 days vs previous 7 days ROAS & CTR."""

        max_date = df["date"].max()

        last_7 = df[df["date"] >= max_date - pd.Timedelta(days=7)]
        prev_7 = df[
            (df["date"] < max_date - pd.Timedelta(days=0))
            & (df["date"] >= max_date - pd.Timedelta(days=14))
        ]

        return {
            "roas_last_7": last_7["roas"].mean(),
            "roas_prev_7": prev_7["roas"].mean(),
            "ctr_last_7": last_7["ctr"].mean(),
            "ctr_prev_7": prev_7["ctr"].mean(),
        }
