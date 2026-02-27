"""
frontend/app.py — Streamlit entry point with session-based navigation.

Run with:
    streamlit run frontend/app.py
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load env so API_BASE is available
load_dotenv()

# ── Page config must be the FIRST streamlit call ───────────────────────────────
st.set_page_config(
    page_title="Salethur Supermarket",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global dark theme override ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #0d1117;
    color: #c9d1d9;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #c9d1d9 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    text-align: left !important;
    width: 100% !important;
    margin-bottom: 6px !important;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(233,69,96,0.15) !important;
    border-color: #e94560 !important;
    color: #e94560 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.06) !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────────
import extra_streamlit_components as stx

# ── Cookie Manager ─────────────────────────────────────────────────────────────
cookie_manager = stx.CookieManager()

# ── Session state defaults ─────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = cookie_manager.get("token")
if "role" not in st.session_state:
    st.session_state.role = cookie_manager.get("role")
if "username" not in st.session_state:
    st.session_state.username = cookie_manager.get("username")
if "user_id" not in st.session_state:
    val = cookie_manager.get("user_id")
    st.session_state.user_id = int(val) if val else None
if "page" not in st.session_state:
    st.session_state.page = cookie_manager.get("page") or "login"


# ── Not logged in → show login ─────────────────────────────────────────────────
if not st.session_state.token:
    from login import show_login
    show_login(cookie_manager)
    st.stop()


# ── Logged in: build sidebar navigation ───────────────────────────────────────
role = st.session_state.role
username = st.session_state.username

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div style="font-size:2rem;">🛒</div>
        <div style="font-size:1.1rem; font-weight:700; color:#fff;">Salethur Supermarket</div>
        <div style="font-size:0.8rem; color:rgba(255,255,255,0.4);">POS + CRM System</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.caption(f"👤 **{username}** &nbsp;&nbsp; 🔑 `{role}`")
    st.divider()

    # ── Navigation buttons ─────────────────────────────────────────────────────
    if st.button("🧾 POS Billing", use_container_width=True):
        st.session_state.page = "pos"
        cookie_manager.set("page", "pos", key="nav_pos")
        st.rerun()

    if role == "admin":
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            cookie_manager.set("page", "dashboard", key="nav_dashboard")
            st.rerun()

        if st.button("📦 Inventory", use_container_width=True):
            st.session_state.page = "inventory"
            cookie_manager.set("page", "inventory", key="nav_inventory")
            st.rerun()

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        for key in ["token", "role", "username", "user_id", "page", "cart"]:
            st.session_state.pop(key, None)
            cookie_manager.delete(key, key=f"delete_{key}")
        st.rerun()

    st.markdown("""
    <div style="position:fixed; bottom:18px; font-size:0.7rem; color:rgba(255,255,255,0.2);">
        E26 Supermarket POS v1.0
    </div>
    """, unsafe_allow_html=True)


# ── Route to the correct page ──────────────────────────────────────────────────
page = st.session_state.get("page", "pos")

if page == "pos":
    from pos import show_pos
    show_pos()

elif page == "dashboard":
    if role != "admin":
        st.error("⛔ Admin access only.")
        st.stop()
    from dashboard import show_dashboard
    show_dashboard()

elif page == "inventory":
    if role != "admin":
        st.error("⛔ Admin access only.")
        st.stop()
    from inventory import show_inventory
    show_inventory()

else:
    st.error("Unknown page. Please use the sidebar to navigate.")
