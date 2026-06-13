import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/srees1988/predict-churn-py/main/customer_churn_data.csv"

FEATURE_COLS = [
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies"
]

def load_raw():
    df = pd.read_csv(DATA_URL)
    # Fix TotalCharges — stored as string with some spaces
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"])
    return df

def engineer_features(df):
    # How many add-on features the client uses (0–6) — proxy for product adoption
    df["features_used"] = df[FEATURE_COLS].apply(
        lambda row: sum(row == "Yes"), axis=1
    )

    # Open support tickets proxy from internet service type
    df["support_tickets_open"] = df["InternetService"].map(
        {"Fiber optic": 3, "DSL": 1, "No": 0}
    )

    # NPS proxy: penalise senior citizens and month-to-month contracts
    df["nps_score"] = 8 - df["SeniorCitizen"] * 2 - (df["Contract"] == "Month-to-month").astype(int)
    df["nps_score"] = df["nps_score"].clip(1, 10)

    # Days to renewal proxy: tenure-based (shorter tenure = sooner renewal risk)
    df["days_to_renewal"] = ((df["tenure"] % 12) * 30).clip(lower=7)

    return df

def load_data():
    df = load_raw()
    df = engineer_features(df)
    return df
