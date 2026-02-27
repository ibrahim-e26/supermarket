"""
frontend/login.py — Streamlit login page.
"""
import streamlit as st
import requests
import os

def get_api_base():
    try:
        return st.secrets["BACKEND_URL"]
    except Exception:
        return os.getenv("BACKEND_URL", os.getenv("API_BASE", "http://localhost:8000"))

API_BASE = get_api_base()


def show_login(cookie_manager):
    st.set_page_config(page_title="Supermarket POS — Login", page_icon="🛒", layout="centered")

    # ── Custom CSS ─────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }

    .login-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        padding: 40px;
        backdrop-filter: blur(12px);
        margin: 40px auto;
        max-width: 420px;
    }

    .login-title {
        text-align: center;
        color: #fff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .login-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.5);
        font-size: 0.9rem;
        margin-bottom: 28px;
    }

    div[data-testid="stForm"] { background: transparent; padding: 0; }

    .stTextInput > label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem; }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: #fff !important;
        padding: 10px 14px !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #e94560, #c23152) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
        padding: 12px 0 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<p class="login-title">🛒 E26 Supermarket</p>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle">Point of Sale & CRM System</p>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("🔐 Login")

    if submitted:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            with st.spinner("Authenticating…"):
                try:
                    resp = requests.post(
                        f"{API_BASE}/auth/login",
                        data={"username": username, "password": password},
                        timeout=5,
                    )
                    if resp.status_code == 200:
                        token_data = resp.json()
                        st.session_state["token"] = token_data["access_token"]
                        st.session_state["role"] = token_data["role"]
                        st.session_state["username"] = token_data["username"]
                        st.session_state["user_id"] = token_data["user_id"]
                        
                        target_page = "pos" if token_data["role"] == "staff" else "dashboard"
                        st.session_state["page"] = target_page

                        # Set cookies with unique keys to avoid StreamlitDuplicateElementKey
                        cookie_manager.set("token", token_data["access_token"], key="set_token")
                        cookie_manager.set("role", token_data["role"], key="set_role")
                        cookie_manager.set("username", token_data["username"], key="set_username")
                        cookie_manager.set("user_id", str(token_data["user_id"]), key="set_user_id")
                        cookie_manager.set("page", target_page, key="set_page")
                        
                        if token_data.get("db_connected"):
                            st.success("✅ database is connected to backend")
                            import time
                            time.sleep(1.5)  # Let user see the message
                        
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Cannot connect to backend. Make sure the API server is running.")

    st.markdown('</div>', unsafe_allow_html=True)
