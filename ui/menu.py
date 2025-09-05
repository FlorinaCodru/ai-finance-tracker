import datetime as dt
import streamlit as st
from finance.repository import FinanceRep

def ai_api_key():
    st.subheader("Gemini API Key")
    st.caption("Enter key here to enable budgeting tips.")
    key_input = st.text_input("API Key", value="", type="password", placeholder="paste key…")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Use Key", use_container_width=True, key="use_key_btn"):
            if key_input.strip():
                st.session_state["gemini_key"] = key_input.strip()
                st.success("API key set for this session.")
            else:
                st.warning("Please paste a valid key.")
    with c2:
        if st.button("Clear Key", use_container_width=True, key="clear_key_btn"):
            st.session_state["gemini_key"] = ""
            st.info("API key cleared (will use .env if set).")

def menu_add_category(repo: FinanceRep):
    st.subheader("Add Category")
    c1, c2 = st.columns([2,1])
    with c1:
        name = st.text_input("Category name", max_chars=50, placeholder="e.g., Salary, Rent, Groceries", key="cat_name")
    with c2:
        typ = st.selectbox("Type", ["EXPENSE","INCOME"], index=0, key="cat_type_add")
    if st.button("Add Category", use_container_width=True, key="add_cat_btn"):
        ok, msg = repo.add_category(name, typ)
        st.success(msg) if ok else st.error(msg)
        if ok: st.rerun()

def menu_add_budget(repo: FinanceRep):
    st.subheader("Budgets (Monthly)")
    cats = repo.list_categories("EXPENSE")
    if cats.empty:
        st.info("Create at least one EXPENSE category to set a budget.")
        return


    id_map = {str(r["name"]): int(r["id"]) for _, r in cats.iterrows()}
    name_options = list(id_map.keys())

    selected_name = st.selectbox("Category", name_options, key="budget_category")
    cat_id = id_map[selected_name]
    limit = st.number_input("Monthly limit", min_value=0.0, step=50.0, key="budget_limit")

    if st.button("Save Budget", use_container_width=True, key="save_budget_btn"):
        ok, msg = repo.add_budget(cat_id, float(limit))
        st.success(msg) if ok else st.error(msg)

def menu_add_trans(repo: FinanceRep):
    st.subheader("Add Transaction")
    today = dt.date.today().isoformat()
    date = st.text_input("Date (YYYY-MM-DD)", value=today, key="txn_date")
    desc = st.text_input("Description", max_chars=120, placeholder="e.g: Coffee, Salary", key="txn_desc")
    amount = st.number_input("Amount", min_value=0.01, step=1.0, key="txn_amount")
    typ = st.selectbox("Type", ["EXPENSE","INCOME"], index=0, key="txn_type_add")

    cat_df = repo.list_categories(typ)
    if cat_df.empty:
        st.warning(f"No {typ} categories yet—add one below.")
        cat_id = None
    else:
       
        id_map = {str(r["name"]): int(r["id"]) for _, r in cat_df.iterrows()}
        name_options = list(id_map.keys())

        selected_name = st.selectbox("Category", name_options, key="txn_category_add")
        cat_id = id_map[selected_name] if selected_name else None

    if st.button("Add", use_container_width=True, type="primary", disabled=(cat_id is None), key="add_txn_btn"):
        ok, msg = repo.add_trans(date, desc, float(amount), cat_id, typ)
        st.success(msg) if ok else st.error(msg)
        if ok: st.rerun()

def render_menu(repo: FinanceRep, service, ai):
    menu_add_trans(repo)
    st.markdown("---")
    menu_add_category(repo)
    st.markdown("---")
    menu_add_budget(repo)
    st.markdown("---")
    ai_api_key()
