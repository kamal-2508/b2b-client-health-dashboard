import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

SYSTEM_PROMPT = """You are a B2B Customer Success AI assistant helping a SaaS company's CS team.
Given a client's health metrics, write a concise 3-part analysis:
1. What the data shows about this client
2. Why they are or aren't at churn risk
3. One specific action the CS team should take this week

Be direct. Use the numbers. Keep it under 120 words."""

def get_client_insight(client: dict, groq_api_key: str = None) -> str:
    api_key = groq_api_key or os.getenv("GROQ_API_KEY")
    llm = ChatGroq(
        api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=200
    )
    user_msg = f"""Client ID: {client['customerID']}
Contract: {client['Contract']}
Monthly Charges: ${client['MonthlyCharges']}
Tenure: {client['tenure']} months
Features Used: {client['features_used']} / 6
NPS Score (proxy): {client['nps_score']} / 10
Open Support Tickets (proxy): {client['support_tickets_open']}
Churn Score: {client['churn_score']} / 100
Risk Tier: {client['risk_tier']}
Actual Churn Label: {client['Churn']}
Days to Renewal: {int(client['days_to_renewal'])}"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg)
    ])
    return response.content