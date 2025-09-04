import streamlit as st
from finance.config import APP_NAME
from finance.db import Database
from finance.repository import Repo
from finance.services import FinanceService
from finance.ai import GeminiService
from ui.theme import inject_theme
from ui.sidebar import render_sidebar
from ui.views import render_filters, render_kpis, render_insights, render_tabs

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="💰", layout="wide", initial_sidebar_state="expanded")
    inject_theme() 

    # --- infra / services ---
    db = Database()
    db.init_db()
    repo = Repo(db)
    service = FinanceService(repo)
    ai = GeminiService()

    st.title(APP_NAME)
    st.caption("Track money, visualize trends, and get concise AI budgeting tips.")

    # Sidebar (right)
    with st.sidebar:
        render_sidebar(repo, service, ai)  

    # Filters
    start, end, typ, cat_ids = render_filters(repo)
    df = repo.fetch_transactions(start, end, typ, cat_ids)

    # KPIs + Insights
    render_kpis(service, df)
    render_insights(service, df)

    # Tabs (Charts / Transactions / AI Advice)
    render_tabs(repo, service, ai, df)

if __name__ == "__main__":
    main()
