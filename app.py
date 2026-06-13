import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.scoring import compute_churn_score, renewal_alerts
from utils.ai_chat import get_client_insight

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B2B SaaS Client Health Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 B2B SaaS — Client Health Dashboard")
st.caption("Customer Success Team View · IBM Telco Open Dataset")

# ── Load & score data ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data...")
def get_scored_data():
    df = load_data()
    df = compute_churn_score(df)
    return df

df = get_scored_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    contract_filter = st.multiselect(
        "Contract Type",
        options=df["Contract"].unique().tolist(),
        default=df["Contract"].unique().tolist()
    )

    risk_filter = st.multiselect(
        "Risk Tier",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )

    tenure_range = st.slider(
        "Tenure (months)",
        min_value=int(df["tenure"].min()),
        max_value=int(df["tenure"].max()),
        value=(int(df["tenure"].min()), int(df["tenure"].max()))
    )

    st.divider()
    st.caption("B2B SaaS Client Health Dashboard · Built with IBM Telco Dataset")

# Apply filters
filtered = df[
    df["Contract"].isin(contract_filter) &
    df["risk_tier"].isin(risk_filter) &
    df["tenure"].between(tenure_range[0], tenure_range[1])
]

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.subheader("Overview")
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Clients",     len(filtered))
k2.metric("High Risk",         int((filtered["risk_tier"] == "High").sum()),
          delta=f"{(filtered['risk_tier']=='High').mean()*100:.1f}% of total",
          delta_color="inverse")
k3.metric("Avg Churn Score",   f"{filtered['churn_score'].mean():.1f}")
k4.metric("Monthly Revenue",   f"${filtered['MonthlyCharges'].sum():,.0f}")
k5.metric("Actual Churn Rate", f"{(filtered['Churn']=='Yes').mean()*100:.1f}%",
          delta_color="inverse")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

RISK_COLORS = {"High": "#E24B4A", "Medium": "#EF9F27", "Low": "#1D9E75"}

with col1:
    st.subheader("Churn Risk by Contract Type")
    risk_contract = (
        filtered.groupby(["Contract", "risk_tier"], observed=True)
        .size()
        .reset_index(name="count")
    )
    fig1 = px.bar(
        risk_contract, x="Contract", y="count",
        color="risk_tier", color_discrete_map=RISK_COLORS,
        barmode="stack",
        labels={"count": "Clients", "risk_tier": "Risk"}
    )
    fig1.update_layout(margin=dict(t=20, b=20), legend_title="Risk Tier")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Feature Adoption vs Churn Score")
    fig2 = px.scatter(
        filtered.sample(min(500, len(filtered)), random_state=42),
        x="features_used", y="churn_score",
        color="risk_tier", color_discrete_map=RISK_COLORS,
        opacity=0.6,
        labels={
            "features_used": "Features Used (0–6)",
            "churn_score": "Churn Score",
            "risk_tier": "Risk"
        },
        hover_data=["customerID", "Contract", "tenure"]
    )
    fig2.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Monthly Revenue at Risk")
    mrr_risk = (
        filtered.groupby("risk_tier", observed=True)["MonthlyCharges"]
        .sum()
        .reset_index()
        .rename(columns={"MonthlyCharges": "MRR"})
    )
    fig3 = px.pie(
        mrr_risk, names="risk_tier", values="MRR",
        color="risk_tier", color_discrete_map=RISK_COLORS,
        hole=0.45
    )
    fig3.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Churn Score Distribution")
    fig4 = px.histogram(
        filtered, x="churn_score", nbins=30,
        color_discrete_sequence=["#378ADD"],
        labels={"churn_score": "Churn Score"}
    )
    fig4.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Renewal Alerts ────────────────────────────────────────────────────────────
st.subheader("⚠️ Renewal Alerts — Due in 60 Days")
alerts = renewal_alerts(filtered, days_threshold=60)

if alerts.empty:
    st.info("No renewals due within the selected filters.")
else:
    st.dataframe(
        alerts,
        use_container_width=True,
        height=220
    )

st.divider()

# ── Client Health Table ───────────────────────────────────────────────────────
st.subheader("Client Health Table")

show_cols = [
    "customerID", "Contract", "MonthlyCharges", "tenure",
    "features_used", "nps_score", "support_tickets_open",
    "churn_score", "risk_tier", "Churn"
]

st.dataframe(
    filtered[show_cols]
    .sort_values("churn_score", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
    height=300
)

st.divider()

# ── AI Risk Explainer ─────────────────────────────────────────────────────────
st.subheader("🤖 AI Client Risk Explainer")
st.caption("Select a high-risk client to get an AI-generated CS action plan")

col_ai1, col_ai2 = st.columns([2, 1])

with col_ai1:
    # Default to showing high-risk clients first
    high_risk_ids = filtered[filtered["risk_tier"] == "High"]["customerID"].tolist()
    all_ids = filtered["customerID"].tolist()
    ordered_ids = high_risk_ids + [c for c in all_ids if c not in high_risk_ids]

    selected_id = st.selectbox("Select a client", ordered_ids)

with col_ai2:
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

client_row = filtered[filtered["customerID"] == selected_id].iloc[0]

# Show client snapshot
with st.expander("Client snapshot", expanded=True):
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Contract",       client_row["Contract"])
    s2.metric("Tenure",         f"{client_row['tenure']} mo")
    s3.metric("Monthly Rev",    f"${client_row['MonthlyCharges']:.0f}")
    s4.metric("Churn Score",    f"{client_row['churn_score']}")
    s5.metric("Risk Tier",      str(client_row["risk_tier"]))

if st.button("Generate AI Insight", type="primary"):
    if not groq_key:
        st.warning("Please enter your Groq API key.")
    else:
        with st.spinner("Analysing client health..."):
            try:
                insight = get_client_insight(client_row.to_dict(), groq_key)
                st.success(insight)
            except Exception as e:
                st.error(f"API error: {e}")
