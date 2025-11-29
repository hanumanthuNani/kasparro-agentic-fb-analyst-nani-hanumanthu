import numpy as np
import pandas as pd


class EvaluatorAgent:
    """
    Evaluates hypotheses using quantitative rules.
    """

    def __init__(self, config):
        self.confidence_min = config.get("confidence_min", 0.6)

    # ---------------------------------------------------------
    # Main API
    # ---------------------------------------------------------
    def evaluate(self, df: pd.DataFrame, hypotheses: list) -> list:
        results = []
        for h in hypotheses:
            score, evidence = self._evaluate_hypothesis(df, h)
            results.append({
                "id": h["id"],
                "description": h["description"],
                "confidence": float(score),
                "evidence": evidence
            })
        return results

    # ---------------------------------------------------------
    # Scoring Logic
    # ---------------------------------------------------------
    def _evaluate_hypothesis(self, df, h):
        h_id = h["id"]

        if h_id == "H1":
            return self._evaluate_roas_drop(df)
        elif h_id == "H2":
            return self._evaluate_ctr_drop(df)
        elif h_id == "H3":
            return self._evaluate_spend_shift(df)
        elif h_id == "H4":
            return self._evaluate_frequency_increase(df)
        elif h_id == "H5":
            return self._evaluate_creative_fatigue(df)

        return 0.3, {"reason": "Unknown hypothesis ID"}

    # ---------------------------------------------------------
    # H1: ROAS Drop
    # ---------------------------------------------------------
    def _evaluate_roas_drop(self, df):
        df_sorted = df.sort_values("date")
        if len(df_sorted) < 2:
            return 0.2, {"error": "Not enough data"}

        roas_change = df_sorted["roas"].iloc[-1] - df_sorted["roas"].iloc[0]

        score = 1 - (roas_change / max(df_sorted["roas"].iloc[0], 0.01))
        score = max(0.0, min(1.0, score))

        return score, {"roas_start": float(df_sorted["roas"].iloc[0]),
                       "roas_end": float(df_sorted["roas"].iloc[-1]),
                       "roas_change": float(roas_change)}

    # ---------------------------------------------------------
    # H2: CTR Drop
    # ---------------------------------------------------------
    def _evaluate_ctr_drop(self, df):
        df_sorted = df.sort_values("date")
        ctr_change = df_sorted["ctr"].iloc[-1] - df_sorted["ctr"].iloc[0]

        score = 1 - (ctr_change / max(df_sorted["ctr"].iloc[0], 0.001))
        score = max(0.0, min(1.0, score))

        return score, {
            "ctr_start": float(df_sorted["ctr"].iloc[0]),
            "ctr_end": float(df_sorted["ctr"].iloc[-1]),
            "ctr_change": float(ctr_change)
        }

    # ---------------------------------------------------------
    # H3: Spend Shift
    # ---------------------------------------------------------
    def _evaluate_spend_shift(self, df):
        grp = df.groupby("campaign_name").agg(spend_sum=("spend", "sum")).reset_index()
        std_spend = grp["spend_sum"].std()

        score = min(1.0, std_spend / (grp["spend_sum"].mean() + 1e-6))

        return score, {
            "spend_std": float(std_spend),
            "spend_mean": float(grp["spend_sum"].mean())
        }

    # ---------------------------------------------------------
    # H4: Frequency Increase
    # (We simulate frequency as impressions/clicks ratio)
    # ---------------------------------------------------------
    def _evaluate_frequency_increase(self, df):
        df["freq"] = df["impressions"] / df["clicks"].replace(0, np.nan)
        df_sorted = df.sort_values("date")

        freq_start = df_sorted["freq"].iloc[0]
        freq_end = df_sorted["freq"].iloc[-1]

        score = min(1.0, (freq_end - freq_start) / max(freq_start, 0.01))

        return score, {
            "freq_start": float(freq_start),
            "freq_end": float(freq_end)
        }

    # ---------------------------------------------------------
    # H5: Creative Fatigue (low purchases + low CTR)
    # ---------------------------------------------------------
    def _evaluate_creative_fatigue(self, df):
        grp = df.groupby("campaign_name").agg(
            ctr_mean=("ctr", "mean"),
            purchases_sum=("purchases", "sum")
        )

        low_ctr = grp["ctr_mean"] < grp["ctr_mean"].mean()
        low_purchase = grp["purchases_sum"] < grp["purchases_sum"].mean()

        fatigue_rate = (low_ctr & low_purchase).mean()

        return fatigue_rate, {
            "fatigue_rate": float(fatigue_rate)
        }
