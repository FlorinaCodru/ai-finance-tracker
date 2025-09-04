import datetime as dt
import pandas as pd
from typing import Tuple
from .repository import Repo

class FinanceService:
    def __init__(self, repo: Repo):
        self.repo = repo
        self.repo.seed_defaults()

    # KPIs
    def kpis(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        if df.empty: return 0.0, 0.0, 0.0
        income = float(df.loc[df["type"]=="INCOME","amount"].sum())
        expense = float(df.loc[df["type"]=="EXPENSE","amount"].sum())
        return income, expense, income-expense

    # Insights (over-budget, top expenses, savings rate)
    def insights(self, df: pd.DataFrame):
        if df.empty:
            return {"savings_rate": None, "top_expenses": [], "over_msgs": []}
        income, expense, net = self.kpis(df)
        savings_rate = (net/income*100.0) if income>0 else None

        ex = df[df["type"]=="EXPENSE"]
        top = ex.groupby("category")["amount"].sum().sort_values(ascending=False).head(3) if not ex.empty else pd.Series(dtype=float)
        top_list = [(c, float(a)) for c,a in top.items()]

        budgets = self.repo.get_budgets()
        over_msgs = []
        if not budgets.empty:
            month_start = dt.date.today().replace(day=1)
            month_end = (month_start + pd.offsets.MonthEnd(0)).date()
            month_df = df[(df["type"]=="EXPENSE") & (df["date"]>=month_start) & (df["date"]<=month_end)]
            actual = month_df.groupby("category")["amount"].sum() if not month_df.empty else pd.Series(dtype=float)

            b = budgets[budgets["type"]=="EXPENSE"][["category","monthly_limit"]].copy()
            b["actual"] = b["category"].map(actual).fillna(0.0)
            over = b[b["actual"] > b["monthly_limit"]]
            for _,r in over.iterrows():
                over_msgs.append(f"Over budget in **{r['category']}** by {(r['actual']-r['monthly_limit']):,.0f}")

        return {"savings_rate": savings_rate, "top_expenses": top_list, "over_msgs": over_msgs}
