"""SmartFinance Streamlit dashboard.

Runs alongside the React frontend and hits the same Flask API.
Launch with: streamlit run smartfinance/ui/streamlit_app.py
"""
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:5000")

st.set_page_config(
    page_title="SmartFinance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----- API client -----

def api_get(path, **kwargs):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"GET {path} failed: {e}")
        return None


def api_post(path, json=None):
    try:
        r = requests.post(f"{API_BASE}{path}", json=json or {}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"POST {path} failed: {e}")
        return None


# ----- Sidebar -----

with st.sidebar:
    st.title("💰 SmartFinance")
    st.caption("Streamlit dashboard")
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📋 Transactions", "🔄 ETL Pipeline", "🤖 ML Predictions", "🔗 Plaid"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"API: `{API_BASE}`")
    health = api_get("/health")
    if health and health.get("status") == "healthy":
        st.success("Backend connected", icon="✅")
    else:
        st.error("Backend offline", icon="❌")


# ----- Helpers -----

@st.cache_data(ttl=10)
def load_transactions(limit=500):
    data = api_get(f"/transactions?limit={limit}")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data.get("transactions", []))
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["year_month"] = df["date"].dt.to_period("M").astype(str)
    return df


# ----- Pages -----

def page_dashboard():
    st.title("Dashboard")
    df = load_transactions(500)

    if df.empty:
        st.info("No transactions loaded. Run the ETL pipeline first (sidebar → ETL Pipeline).")
        return

    total = df["amount"].sum()
    avg = df["amount"].mean()
    n_cat = df["category"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", f"{len(df):,}")
    c2.metric("Total spend", f"${total:,.2f}")
    c3.metric("Avg transaction", f"${avg:,.2f}")
    c4.metric("Categories", n_cat)

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Spend by category")
        cat = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
        fig = px.bar(cat, x="category", y="amount", color="category", text_auto=".2s")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Monthly spend")
        monthly = df.groupby("year_month", as_index=False)["amount"].sum().sort_values("year_month")
        fig2 = px.line(monthly, x="year_month", y="amount", markers=True)
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top merchants")
    top = (df.groupby("name", as_index=False)["amount"]
             .sum().sort_values("amount", ascending=False).head(10))
    fig3 = px.bar(top, x="amount", y="name", orientation="h", text_auto=".2s")
    fig3.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)


def page_transactions():
    st.title("Transactions")
    df = load_transactions(1000)

    if df.empty:
        st.info("No transactions yet. Run ETL or link an account.")
        return

    with st.expander("Filters", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
            cat_sel = st.selectbox("Category", categories)
        with c2:
            min_amt = float(df["amount"].min())
            max_amt = float(df["amount"].max())
            amt_range = st.slider("Amount range", min_amt, max_amt, (min_amt, max_amt))
        with c3:
            search = st.text_input("Search name", "")

    filtered = df.copy()
    if cat_sel != "All":
        filtered = filtered[filtered["category"] == cat_sel]
    filtered = filtered[(filtered["amount"] >= amt_range[0]) & (filtered["amount"] <= amt_range[1])]
    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]

    st.caption(f"Showing {len(filtered)} of {len(df)} transactions")
    st.dataframe(
        filtered[["date", "name", "category", "amount", "merchant_name"]].sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, f"transactions-{datetime.now():%Y%m%d}.csv", "text/csv")


def page_etl():
    st.title("ETL Pipeline")
    st.write(
        "Extract → Transform → Load. Reads a CSV, normalizes, "
        "enriches with calendar features, persists to the database."
    )

    source = st.text_input("Source path", "data/sample_transactions.csv")
    if st.button("Run pipeline", type="primary"):
        with st.spinner("Running ETL..."):
            result = api_post("/etl/run", {"source": source})
        if result and result.get("ok"):
            st.success(f"Loaded {result['rows_loaded']} rows from {result['rows_extracted']} extracted")
            load_transactions.clear()
            st.subheader("Monthly summaries")
            summaries = result.get("monthly_summaries", [])
            if summaries:
                st.dataframe(pd.DataFrame(summaries), use_container_width=True, hide_index=True)
        elif result:
            st.error(result.get("error", "ETL failed"))


def page_ml():
    st.title("ML — Overspending prediction")
    st.write("Logistic regression on monthly spend features. Train first, then predict.")

    st.subheader("1. Train")
    if st.button("Train model", type="primary"):
        with st.spinner("Training..."):
            metrics = api_post("/ml/train")
        if metrics and metrics.get("ok"):
            st.success("Model trained ✓")
            cols = st.columns(4)
            for i, k in enumerate(["accuracy", "precision", "recall", "f1"]):
                if k in metrics:
                    cols[i].metric(k.capitalize(), f"{metrics[k]:.2%}")
            st.caption(f"Samples: {metrics.get('samples')} · Model path: `{metrics.get('model_path')}`")
        elif metrics:
            st.error(metrics.get("error", "Training failed"))

    st.divider()
    st.subheader("2. Predict")
    c1, c2, c3 = st.columns(3)
    monthly_spend = c1.number_input("Monthly spend ($)", value=2500.0, step=100.0)
    txn_count = c1.number_input("Transaction count", value=35, step=1)
    avg_txn = c2.number_input("Avg transaction ($)", value=71.4, step=1.0)
    max_txn = c2.number_input("Max transaction ($)", value=320.0, step=10.0)
    weekend_ratio = c3.slider("Weekend ratio", 0.0, 1.0, 0.3)
    category_diversity = c3.number_input("Category diversity", value=6, step=1)

    if st.button("Predict overspend risk"):
        features = {
            "monthly_spend": monthly_spend,
            "txn_count": txn_count,
            "avg_txn": avg_txn,
            "max_txn": max_txn,
            "weekend_ratio": weekend_ratio,
            "category_diversity": category_diversity,
        }
        with st.spinner("Predicting..."):
            result = api_post("/ml/predict", features)
        if result and result.get("ok"):
            prob = result["overspend_probability"]
            risk = result["risk_level"]
            color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk, "⚪")
            c1, c2 = st.columns(2)
            c1.metric("Overspend probability", f"{prob:.1%}")
            c2.metric("Risk level", f"{color} {risk.upper()}")
            st.progress(prob)
        elif result:
            st.error(result.get("error", "Prediction failed"))


def page_plaid():
    st.title("Plaid integration")
    st.write(
        "Plaid Link is a JS-only widget — easiest way to link an account "
        "is the React UI at http://localhost:3000."
    )

    st.subheader("Create a sandbox link token")
    if st.button("Generate link token"):
        result = api_post("/create_link_token")
        if result and "link_token" in result:
            st.success("Link token created")
            st.code(result["link_token"], language="text")

    st.subheader("Fetch transactions from linked account")
    st.caption("This requires you to have linked an account via the React UI first.")
    if st.button("Pull latest from Plaid"):
        result = api_get("/get_transactions")
        if result and "transactions" in result:
            st.success(f"Fetched {result['count']} transactions")
            st.dataframe(pd.DataFrame(result["transactions"]), use_container_width=True, hide_index=True)


# ----- Router -----

PAGES = {
    "📊 Dashboard": page_dashboard,
    "📋 Transactions": page_transactions,
    "🔄 ETL Pipeline": page_etl,
    "🤖 ML Predictions": page_ml,
    "🔗 Plaid": page_plaid,
}

PAGES[page]()
