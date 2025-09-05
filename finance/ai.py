import os
import streamlit as st
import pandas as pd
from .services import FinanceService
from .repository import FinanceRep
from dotenv import load_dotenv


try:
    import google.generativeai as genai
except Exception:
    genai = None

load_dotenv()
ENV_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class AiService:
    def __init__(self):
        pass

    def api_key(self) -> str:
        return st.session_state.get("gemini_key","") or ENV_GEMINI_API_KEY

    def init(self):
        if not genai:
            return False, "google generativeai not installed."
        key = self.api_key()
        if not key:
            return False, "GEMINI_API_KEY not set."
        try:
            genai.configure(api_key=key)
            return True, ""
        except Exception as e:
            return False, f"{e}"

    def make_prompt(self, df: pd.DataFrame, months: int, finance: FinanceService) -> str:
        if df.empty:
            return "User has no data."
        cutoff = (pd.Timestamp.today().date().replace(day=1) - pd.offsets.MonthBegin(months)).date()
        recent = df[df["date"] >= cutoff].copy()
        if recent.empty:
            recent = df.copy()

        income = recent[recent["type"]=="INCOME"].groupby("category")["amount"].sum().sort_values(ascending=False).to_dict()
        expense = recent[recent["type"]=="EXPENSE"].groupby("category")["amount"].sum().sort_values(ascending=False).to_dict()
        total_income = sum(income.values()); total_expense = sum(expense.values()); net = total_income-total_expense

        def lines(d): return "\n".join([f"- {k}: {v:.2f}" for k,v in d.items()])

        return f"""
You are a budgeting coach. Based on the user's recent income and expenses, give concise, practical budgeting recommendations.

Timeframe: last ~{months} months (or available recent data)
Currency: Treat amounts as generic units; do not assume a country
Style: bullet points, specific, actionable, keep it short and helpful. Avoid generic filler.

Summary:
- Total income: {total_income:.2f}
- Total expense: {total_expense:.2f}
- Net: {net:.2f}

Income by category:
{lines(income) if income else "- (none)"}

Expenses by category:
{lines(expense) if expense else "- (none)"}

Constraints:
- Focus on category-level opportunities (e.g., “trim dining by 15%”)
- Suggest 2–4 steps to improve savings next month
- If data is sparse, give starter advice (50/30/20 rule, emergency fund, etc.)
""".strip()

    def get_advice(self, prompt: str, model_name: str = "gemini-1.5-pro") -> str:
        ok, msg = self.init()
        if not ok:
            return f" AI advice unavailable: {msg}"
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            return (getattr(resp,"text","") or "").strip() or "No advice returned"
        except Exception as e:
            return f"AI advice error: {e}"
