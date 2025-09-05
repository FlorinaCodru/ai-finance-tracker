import streamlit as st
from finance.config import APP_NAME
from finance.db import FinanceDb
from finance.repository import FinanceRep
from finance.services import FinanceService
from finance.ai import AiService
from ui.theme import inject_theme
from ui.menu import render_menu
from ui.views import show_filters, display_kpis, show_finance_insights, all_tabs

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="💰", layout="wide", initial_sidebar_state="expanded")
    inject_theme() 

    # --- infra / services ---
    db = FinanceDb()
    db.init_db()
    repo = FinanceRep(db)
    service = FinanceService(repo)
    ai = AiService()

    st.title(APP_NAME)
   

    # Sidebar (right)
    with st.sidebar:
        render_menu(repo, service, ai)  

    # Filters
    start, end, typ, cat_ids = show_filters(repo)
    df = repo.get_trans(start, end, typ, cat_ids)

    # KPIs + finance_insights
    display_kpis(service, df)
    show_finance_insights(service, df)

    # Tabs (Charts / Transactions / AI Advice)
    all_tabs(repo, service, ai, df)

if __name__ == "__main__":
    main()
