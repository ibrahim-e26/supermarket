"""
frontend/dashboard.py — Admin analytics dashboard.
"""
import streamlit as st
import requests
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

def get_api_base():
    try:
        return st.secrets["BACKEND_URL"]
    except Exception:
        return os.getenv("BACKEND_URL", os.getenv("API_BASE", "http://localhost:8000"))

API_BASE = get_api_base()


def _headers():
    return {"Authorization": f"Bearer {st.session_state.get('token', '')}"}


def _api(path):
    try:
        resp = requests.get(f"{API_BASE}{path}", headers=_headers(), timeout=8)
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


def show_dashboard():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .dash-header { font-size: 1.5rem; font-weight: 700;
                    background: linear-gradient(90deg,#e94560,#c23152); color:#fff;
                    padding:14px 20px; border-radius:12px; margin-bottom:16px; }
    .kpi-card { background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
                 border-radius:14px; padding:18px; text-align:center; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #e94560; }
    .kpi-label { color: rgba(200,200,200,0.7); font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="dash-header">📊 Admin Dashboard</div>', unsafe_allow_html=True)

    # Date picker
    selected_date = st.date_input("📅 Select Date", value=date.today())

    # ── Daily Summary ─────────────────────────────────────────────────────────
    summary = _api(f"/dashboard/summary?target_date={selected_date}")
    if summary:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Revenue", f"₹{summary['total_revenue']:,.2f}")
        c2.metric("🧾 Transactions", summary["total_transactions"])
        pb = summary.get("payment_breakdown", {})
        c3.metric("💵 Cash", f"₹{pb.get('cash', 0):,.2f}")
        c4.metric("📱 UPI", f"₹{pb.get('upi', 0):,.2f}")

        # Payment breakdown donut chart
        breakdown = {k: v for k, v in pb.items() if v > 0}
        if breakdown:
            fig = go.Figure(data=[go.Pie(
                labels=list(breakdown.keys()),
                values=list(breakdown.values()),
                hole=0.55,
                marker_colors=["#e94560", "#0f3460", "#533483", "#2ecc71"],
            )])
            fig.update_layout(
                title="Payment Breakdown",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                margin=dict(t=40, b=10, l=10, r=10),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col_top, col_low = st.columns(2)

    # ── Top Products ──────────────────────────────────────────────────────────
    with col_top:
        st.subheader("🏆 Top Products (All Time)")
        top = _api("/dashboard/top-products?limit=8")
        if top:
            df_top = pd.DataFrame(top)
            fig = px.bar(
                df_top,
                x="total_revenue",
                y="product_name",
                orientation="h",
                color="total_revenue",
                color_continuous_scale=["#0f3460", "#e94560"],
                labels={"total_revenue": "Revenue (₹)", "product_name": "Product"},
                text="total_qty",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc",
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                margin=dict(t=20, b=10, l=10, r=10),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")

    # ── Low Stock Alerts ──────────────────────────────────────────────────────
    with col_low:
        st.subheader("⚠️ Low Stock Alerts")
        low = _api("/dashboard/low-stock")
        if low:
            df_low = pd.DataFrame(low)
            st.dataframe(
                df_low.style.applymap(
                    lambda v: "color: #e94560; font-weight: bold"
                    if isinstance(v, (int, float)) and v < 5 else "",
                    subset=["stock_qty"],
                ),
                use_container_width=True,
                height=300,
            )
        else:
            st.success("✅ All products have adequate stock.")

    st.divider()

    # ── Monthly Revenue Chart ─────────────────────────────────────────────────
    st.subheader("📈 Monthly Revenue")
    monthly = _api("/dashboard/monthly-revenue")
    if monthly:
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        df_m = pd.DataFrame(monthly)
        df_m["month_name"] = df_m["month"].apply(lambda m: months[int(m)-1])
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_m["month_name"], y=df_m["revenue"],
            name="Revenue",
            marker_color="#e94560",
        ))
        fig.add_trace(go.Scatter(
            x=df_m["month_name"], y=df_m["transactions"],
            name="Transactions",
            mode="lines+markers",
            marker_color="#0f3460",
            yaxis="y2",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            yaxis=dict(title=dict(text="Revenue (₹)", font=dict(color="#e94560"))),
            yaxis2=dict(title=dict(text="Transactions", font=dict(color="#0f3460")), overlaying="y", side="right"),
            height=340,
            margin=dict(t=20, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Credit Summary ────────────────────────────────────────────────────────
    st.subheader("🤝 Outstanding Credits")
    credits = _api("/dashboard/credit-summary")
    if credits:
        df_credit = pd.DataFrame(credits)
        st.dataframe(df_credit, use_container_width=True)
    else:
        st.success("✅ No outstanding credits.")
