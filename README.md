# B2B SaaS Client Health Dashboard

A Customer Success dashboard for B2B SaaS teams — tracks client churn risk, feature adoption, renewal alerts, and generates AI-powered action plans per client.

**Live Demo:** [Hugging Face Spaces](#) <!-- replace with your HF link -->

---

## Problem Statement

Customer Success teams in B2B SaaS companies struggle to identify which clients are at risk of churning before it's too late. This dashboard centralises key health signals into one view and uses AI to generate actionable CS recommendations per client.

## User Persona

**Customer Success Manager** at a B2B SaaS company who needs to:
- Prioritise which clients to reach out to this week
- Understand why a client is at risk
- Get a concrete next action without digging through raw data

## Features

| Feature | Description |
|---|---|
| Churn Score (0–100) | Weighted score based on tenure, feature adoption, NPS proxy, support tickets, contract type |
| Risk Tier | High / Medium / Low classification |
| Renewal Alerts | Clients with renewal due in 60 days |
| Sidebar Filters | Filter by contract type, risk tier, tenure range |
| KPI Cards | Total clients, high-risk count, avg churn score, MRR, actual churn rate |
| Charts | Risk by contract, feature adoption scatter, MRR at risk pie, score distribution |
| AI Risk Explainer | Per-client insight + CS action plan via Groq LLM (LangChain) |

## Tech Stack

- **Frontend:** Streamlit
- **Data processing:** Pandas
- **Visualisation:** Plotly
- **AI layer:** LangChain + Groq API (llama-3.1-8b-instant)
- **Dataset:** IBM Telco Customer Churn (open source, 7,043 rows)
- **Deployment:** Hugging Face Spaces

## Project Structure

```
b2b_dashboard/
├── app.py                  # Main Streamlit app
├── requirements.txt
└── utils/
    ├── data_loader.py      # Data fetch, cleaning, feature engineering
    ├── scoring.py          # Churn score + renewal alert logic
    └── ai_chat.py          # Groq API integration via LangChain
```

## Churn Score Formula

| Signal | Weight | Logic |
|---|---|---|
| Tenure | 25% | Shorter tenure = higher risk |
| Feature adoption | 25% | Fewer features used = higher risk |
| NPS proxy | 20% | Lower NPS = higher risk |
| Support tickets | 15% | More open tickets = higher risk |
| Contract type | 15% | Month-to-month = higher risk |

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/b2b-client-health-dashboard
cd b2b-client-health-dashboard
pip install -r requirements.txt
streamlit run app.py
```

You will need a free [Groq API key](https://console.groq.com) for the AI feature.

## Dataset

IBM Telco Customer Churn — open source dataset, 7,043 customers, 21 columns.  
Source: `https://raw.githubusercontent.com/srees1988/predict-churn-py/main/customer_churn_data.csv`

---

*Built as part of a B2B SaaS product portfolio project.*
