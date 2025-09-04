import datetime as dt
import streamlit as st
import pandas as pd
from typing import Optional, List, Tuple
from finance.repository import Repo
from finance.services import FinanceService
from finance.ai import GeminiService
from ui.charts import category_pie, monthly_trend, budget_vs_actual

def render_filters(repo: Repo) -> Tuple[str, str, Optional[str], List[int]]:
    st.subheader("Filters")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        start = st.text_input("Start date (YYYY-MM-DD)", value=(dt.date.today()-dt.timedelta(days=90)).isoformat(), key="f_start")
    with c2:
        end = st.text_input("End date (YYYY-MM-DD)", value=dt.date.today().isoformat(), key="f_end")
    with c3:
        typ = st.selectbox("Type (optional)", ["All","EXPENSE","INCOME"], index=0, key="f_type")
        typ = None if typ=="All" else typ
    cats = repo.list_categories()
    cat_choices: List[int] = []
    if not cats.empty:
        cat_map = {f"{r['name']} ({r['type']}) [id:{r['id']}]": int(r["id"]) for _,r in cats.iterrows()}
        selected = st.multiselect("Categories (optional)", list(cat_map.keys()), key="f_cats")
        cat_choices = [cat_map[s] for s in selected]
    return start, end, typ, cat_choices

def render_kpis(service: FinanceService, df: pd.DataFrame):
    income, expense, net = service.kpis(df)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-box"><div class="kpi-title">Total Income</div>'
                    f'<div class="kpi-value">{income:,.2f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box"><div class="kpi-title">Total Expenses</div>'
                    f'<div class="kpi-value">{expense:,.2f}</div></div>', unsafe_allow_html=True)
    with c3:
        cls = "good" if net>0 else ("bad" if net<0 else "neutral")
        st.markdown(f'<div class="metric-box"><div class="kpi-title">Net</div>'
                    f'<div class="kpi-value {cls}">{net:,.2f}</div></div>', unsafe_allow_html=True)

def render_insights(service: FinanceService, df: pd.DataFrame):
  
    if df.empty:
        return

    data = service.insights(df)

    # Build lines
    savings_line = ""
    if data["savings_rate"] is not None:
        savings_line = f"<p><b>Savings rate:</b> {data['savings_rate']:.1f}%</p>"

    top_line = ""
    if data["top_expenses"]:
        top_line = "<p><b>Top expenses:</b> " + ", ".join(
            [f"{c} ({amt:,.0f})" for c, amt in data["top_expenses"]]
        ) + "</p>"

    if data["over_msgs"]:
        # over_msgs contain markdown **…** — strip the asterisks so it looks clean in HTML
        over_items = "".join(
            [f"<li class='bad small'>{m.replace('**','')}</li>" for m in data["over_msgs"]]
        )
        over_html = f"<ul>{over_items}</ul>"
    else:
        over_html = "<span class='good small'>No categories over budget this month.</span>"

    # Everything is rendered INSIDE the card in a single HTML block
    html = f"""
    <div class="enhanced-card padded">
      <div class="section-title">Quick Insights</div>
      {savings_line}
      {top_line}
      {over_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_tabs(repo: Repo, service: FinanceService, ai: GeminiService, df: pd.DataFrame):
    t1, t2, t3 = st.tabs(["📊 Charts", "🧾 Transactions", "🤖 AI Advice"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Category Spend (Expenses)**")
            category_pie(df)
        with c2:
            st.markdown("**Monthly Trend (Income vs Expense)**")
            monthly_trend(df)
        st.markdown("---")
        st.markdown("**Budget vs Actual (This Month)**")
        budgets = repo.get_budgets()
        month = dt.date.today().replace(day=1)
        budget_vs_actual(df, budgets, month)

    with t2:
        st.subheader("Transactions")
        if df.empty:
            st.info("No transactions found for the selected filters.")
        else:
            show = df.rename(columns={"id":"ID","date":"Date","description":"Description","amount":"Amount","category":"Category","type":"Type"})
            st.dataframe(show[["ID","Date","Type","Category","Description","Amount"]], use_container_width=True)

            with st.expander("Edit / Delete"):
                txn_ids = df["id"].tolist()
                chosen = st.selectbox("Pick a transaction to edit/delete (by ID)", txn_ids, key="edit_pick")
                row = df[df["id"]==chosen].iloc[0]

                e1, e2 = st.columns(2)
                with e1:
                    date = st.text_input("Date", value=str(row["date"]), key="edit_date")
                    description = st.text_input("Description", value=row["description"] or "", key="edit_desc")
                    amount = st.number_input("Amount", value=float(row["amount"]), min_value=0.01, step=1.0, key="edit_amount")
                with e2:
                    typ = st.selectbox("Type", ["EXPENSE","INCOME"], index=0 if row["type"]=="EXPENSE" else 1, key=f"edit_type_{int(chosen)}")
                    cats = repo.list_categories(typ)
                    cat_label = f"{row['category']} (id:{row['category_id']})"
                    options = [f"{r['name']} (id:{r['id']})" for _,r in cats.iterrows()] or [cat_label]
                    new_cat = st.selectbox("Category", options, index=options.index(cat_label) if cat_label in options else 0, key=f"edit_category_{int(chosen)}")
                    new_cat_id = int(new_cat.split("id:")[-1].strip(")"))

                colb1, colb2, _ = st.columns([1,1,4])
                if colb1.button("Update", type="primary", key="edit_update"):
                    ok, msg = repo.update_transaction(int(chosen), date, description, float(amount), new_cat_id, typ)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()
                if colb2.button("Delete", type="secondary", key="edit_delete"):
                    repo.delete_transaction(int(chosen))
                    st.warning("Transaction deleted.")
                    st.rerun()

        # export
        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", data=csv, file_name="transactions.csv", mime="text/csv")

    with t3:
        st.markdown("**Generate concise budgeting suggestions based on your recent data.**")
        months = st.slider("Summarize roughly how many months?", min_value=1, max_value=12, value=3, key="ai_months")
        if st.button("Get AI Advice", type="primary", key="ai_btn"):
            prompt = ai.build_prompt(df, months, service)
            with st.spinner("Getting tips..."):
                advice = ai.get_advice(prompt)
            st.markdown(advice)
