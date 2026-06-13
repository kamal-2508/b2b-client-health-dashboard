import pandas as pd

def compute_churn_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Churn score 0–100. Higher = more at risk.
    Signals: low tenure, low features used, low NPS, high support tickets,
             month-to-month contract.
    """
    df = df.copy()

    # Normalise each signal to 0–1 (higher = more risk)
    df["s_tenure"]   = 1 - (df["tenure"] / df["tenure"].max())
    df["s_features"] = 1 - (df["features_used"] / 6)
    df["s_nps"]      = 1 - (df["nps_score"] / 10)
    df["s_tickets"]  = df["support_tickets_open"] / 3
    df["s_contract"] = (df["Contract"] == "Month-to-month").astype(float)

    # Weighted churn score
    df["churn_score"] = (
        df["s_tenure"]   * 0.25 +
        df["s_features"] * 0.25 +
        df["s_nps"]      * 0.20 +
        df["s_tickets"]  * 0.15 +
        df["s_contract"] * 0.15
    ) * 100

    df["churn_score"] = df["churn_score"].round(1)

    df["risk_tier"] = pd.cut(
        df["churn_score"],
        bins=[0, 33, 66, 100],
        labels=["Low", "Medium", "High"]
    )

    # Drop intermediate signal columns
    df = df.drop(columns=["s_tenure", "s_features", "s_nps", "s_tickets", "s_contract"])

    return df


def renewal_alerts(df: pd.DataFrame, days_threshold: int = 60) -> pd.DataFrame:
    """Return clients whose renewal is due within days_threshold days."""
    alerts = df[df["days_to_renewal"] <= days_threshold].copy()
    return alerts.sort_values("days_to_renewal")[
        ["customerID", "Contract", "MonthlyCharges", "days_to_renewal",
         "churn_score", "risk_tier"]
    ]
