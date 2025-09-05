import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from finance.config import YELLOW_COLORS

def pie_category(df: pd.DataFrame):
    ex = df[df["type"]=="EXPENSE"]
    if ex.empty:
        st.info("No expense data to plot."); return
    by_cat = ex.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(4.5,4.5))
    colors = (YELLOW_COLORS * ((len(by_cat)//len(YELLOW_COLORS))+1))[:len(by_cat)]
    ax.pie(by_cat.values, labels=by_cat.index, autopct="%1.1f%%", startangle=90, colors=colors)
    ax.axis("equal")
    st.pyplot(fig)

def monthly_trend(df: pd.DataFrame):
    if df.empty:
        st.info("No data to plot."); return
    tmp = df.copy()
    tmp["month"] = pd.to_datetime(tmp["date"]).values.astype("datetime64[M]")
    g = tmp.groupby(["month","type"])["amount"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7,4))
    for typ in ("INCOME","EXPENSE"):
        sub = g[g["type"]==typ]
        if not sub.empty:
            ax.plot(sub["month"], sub["amount"], marker="o", label=typ)
    ax.set_xlabel("Month"); ax.set_ylabel("Amount"); ax.legend(); ax.grid(True, alpha=0.3)
    st.pyplot(fig)

def actual_budget(df: pd.DataFrame, budgets: pd.DataFrame, for_month: dt.date):
    if budgets.empty:
        st.info("No budgets configured."); return
    start = for_month.replace(day=1)
    end = (start + pd.offsets.MonthEnd(0)).date()
    month_df = df[(df["type"]=="EXPENSE") & (df["date"]>=start) & (df["date"]<=end)]
    actual_by_cat = month_df.groupby("category")["amount"].sum() if not month_df.empty else pd.Series(dtype=float)

    plot_df = budgets[budgets["type"]=="EXPENSE"][["category","monthly_limit"]].copy()
    plot_df["actual"] = plot_df["category"].map(actual_by_cat).fillna(0.0)
    if plot_df.empty:
        st.info("No expense budgets configured."); return

    fig, ax = plt.subplots(figsize=(7,4))
    x = range(len(plot_df))
    ax.bar(x, plot_df["monthly_limit"], label="Budget", alpha=0.6, edgecolor="#eab308")
    ax.bar(x, plot_df["actual"], label="Actual", alpha=0.9, edgecolor="#b45309")
    ax.set_xticks(list(x)); ax.set_xticklabels(plot_df["category"], rotation=20, ha="right")
    ax.set_ylabel("Amount"); ax.set_title(f"Budget vs Actual — {for_month.strftime('%B %Y')}")
    ax.legend(); ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)
