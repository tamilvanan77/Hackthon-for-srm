"""
AI Early Warning System for Student Dropout Risk
Main Streamlit Application - Multi-Page Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.risk_model import DropoutRiskModel
from backend.interventions import (
    recommend_interventions,
    get_intervention_effectiveness,
    INTERVENTION_CATALOG,
)
from backend.message_generator import (
    generate_parent_message,
    generate_whatsapp_message,
)
from backend.scheme_matcher import match_schemes, get_scheme_summary
from backend.chatbot import generate_chatbot_response

# ===================================================================
# PAGE CONFIG
# ===================================================================
st.set_page_config(
    page_title="SafePath AI — Student Dropout Risk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===================================================================
# INJECT ANIMATED BACKGROUND
# ===================================================================
import streamlit.components.v1 as components

def inject_animated_background():
    base = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(base, "static", "background.html")
    if os.path.exists(bg_path):
        with open(bg_path, "r", encoding="utf-8") as f:
            bg_html = f.read()
        # We inject the HTML and CSS to position it absolutely covering the screen inside Streamlit's iframe
        components.html(
            f"""
            <style>
                body {{ margin: 0; padding: 0; overflow: hidden; }}
                /* Ensure iframe is transparent */
                html, body {{ background: transparent !important; }}
            </style>
            {bg_html}
            <script>
                // Tell parent streamlit to make this iframe full screen and fixed securely
                const parent = window.parent.document;
                const iframes = parent.getElementsByTagName('iframe');
                for (let i = 0; i < iframes.length; i++) {{
                    if (iframes[i].contentDocument === document) {{
                        const container = iframes[i].parentElement;
                        container.style.position = 'fixed';
                        container.style.top = '0';
                        container.style.left = '0';
                        container.style.width = '100vw';
                        container.style.height = '100vh';
                        container.style.zIndex = '-1';
                        iframes[i].style.width = '100vw';
                        iframes[i].style.height = '100vh';
                        break;
                    }}
                }}
            </script>
            """,
            height=0,
            width=0,
        )

inject_animated_background()

# ===================================================================
# CUSTOM CSS
# ===================================================================
st.markdown("""
<style>
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Apply 'Outfit' font to all Navigation elements, Buttons, and Headings for a 'Luxe' feel */
    h1, h2, h3, h4, .main-title, .section-header, button, .stTabs [data-baseweb="tab"], .role-pill, .topnav-user {
        font-family: 'Outfit', sans-serif !important;
    }

    /* ---- Hide native Streamlit chrome ---- */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    /* hide native sidebar collapse button */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    /* collapse sidebar by default but allow Streamlit to still bind widgets */
    [data-testid="stSidebar"] {
        background: rgba(10, 16, 32, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(79,139,249,0.12) !important;
    }

    /* ---- Page Load & Stagger Animations ---- */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Apply cascading fade-in to the main container and all major un-targeted blocks */
    [data-testid="block-container"], .section-header, .kpi-card, [data-testid="stVerticalBlockBorderWrapper"] {
        animation: fadeInUp 0.5s ease-out forwards;
        animation-fill-mode: both;
    }
    
    /* ---- Custom Glowing Scrollbars ---- */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.2); 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(79, 139, 249, 0.4); 
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.8); 
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    /* ---- Top Navbar ---- */
    #custom-topnav {
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 56px;
        z-index: 99999;
        display: flex;
        align-items: center;
        padding: 0 20px;
        gap: 14px;
        background: rgba(6, 11, 23, 0.82);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(79, 139, 249, 0.18);
        box-shadow: 0 2px 20px rgba(0,0,0,0.35);
    }
    #sidebar-toggle {
        background: none;
        border: 1px solid rgba(79,139,249,0.3);
        border-radius: 8px;
        color: #4F8BF9;
        font-size: 1.15rem;
        width: 36px; height: 36px;
        cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: background 0.2s, border-color 0.2s;
        flex-shrink: 0;
    }
    #sidebar-toggle:hover {
        background: rgba(79,139,249,0.12);
        border-color: rgba(79,139,249,0.6);
    }
    #topnav-logo {
        font-size: 1.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
        flex: 1;
        letter-spacing: 0.5px;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    #topnav-right {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-shrink: 0;
    }
    .topnav-user {
        color: #e2e8f0;
        font-size: 0.85rem;
        font-weight: 500;
        white-space: nowrap;
    }
    .role-pill {
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.3s;
        text-decoration: none;
        display: inline-block;
        letter-spacing: 0.3px;
    }
    .role-pill-active {
        background: linear-gradient(135deg, #4F8BF9, #38bdf8);
        color: white;
        border-color: transparent;
        box-shadow: 0 4px 12px rgba(79, 139, 249, 0.4);
    }
    .role-pill-inactive {
        background: rgba(30, 41, 59, 0.5);
        color: #94a3b8;
        border-color: rgba(79,139,249,0.3);
    }
    .role-pill-inactive:hover {
        border-color: rgba(56, 189, 248, 0.8);
        color: #ffffff;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }
    .topnav-logout {
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        cursor: pointer;
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.3);
        color: #ef4444;
        transition: all 0.2s;
        text-decoration: none;
        display: inline-block;
    }
    .topnav-logout:hover {
        background: rgba(239,68,68,0.25);
        border-color: rgba(239,68,68,0.6);
    }

    /* ---- Push main content below navbar ---- */
    [data-testid="stAppViewContainer"] {
        padding-top: 56px !important;
    }
    [data-testid="block-container"] {
        padding-top: 1.5rem !important;
    }

    /* ---- Background transparent ---- */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ---- DataFrame (Table) Glassmorphic Overrides ---- */
    [data-testid="stDataFrame"] > div {
        background-color: transparent !important;
    }
    /* Hide the gross internal border */
    [data-testid="stDataFrame"] [data-testid="stTable"] {
        background-color: transparent !important;
    }
    /* Style cells */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
        border-right: none !important;
        color: #e2e8f0 !important;
        padding: 12px 16px !important;
        transition: background-color 0.2s;
    }
    /* Hover highlight for rows */
    [data-testid="stDataFrame"] tr:hover td {
        background-color: rgba(79, 139, 249, 0.15) !important;
    }
    /* Header specific styles */
    [data-testid="stDataFrame"] th {
        background-color: rgba(30, 41, 59, 0.8) !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
        border-bottom: 2px solid rgba(79, 139, 249, 0.3) !important;
    }
    /* Attempt to hide row index numbers if they render as th */
    [data-testid="stDataFrame"] th:first-child, [data-testid="stDataFrame"] td:first-child {
        display: none !important; 
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-size: 0.9rem;
    }

    /* ---- Glassmorphic Containers (st.container(border=True)) ---- */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(15, 23, 42, 0.45) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(79, 139, 249, 0.2) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover > div {
        box-shadow: 0 12px 40px 0 rgba(79, 139, 249, 0.15) !important;
        border-color: rgba(79, 139, 249, 0.4) !important;
    }

    /* ---- Premium Inputs (Text, Number, Selectbox) ---- */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #4F8BF9 !important;
        box-shadow: 0 0 0 2px rgba(79, 139, 249, 0.25) !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
    }
    /* Fix selectbox dropdown arrow area */
    .stSelectbox > div > div > div > div:last-child {
        color: #94a3b8 !important;
    }

    /* ---- Premium Buttons ---- */
    /* Primary Button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4F8BF9 0%, #38bdf8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 14px 0 rgba(79, 139, 249, 0.39) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 139, 249, 0.6) !important;
    }
    button[kind="primary"]:active {
        transform: translateY(0) !important;
    }
    /* Secondary/Default Button */
    button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(8px) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    button[kind="secondary"]:hover {
        background: rgba(47, 63, 86, 0.8) !important;
        border-color: rgba(56, 189, 248, 0.8) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2) !important;
    }

    /* ---- Mobile Responsiveness ---- */
    @media (max-width: 768px) {
        .kpi-value { font-size: 2.0rem; }
        .kpi-card { padding: 16px; margin-bottom: 12px; }
        #custom-topnav { padding: 0 10px; gap: 8px; }
        #topnav-logo { font-size: 0.95rem; }
        [data-testid="block-container"] { padding: 1rem 0.5rem !important; }
        .section-header { font-size: 1.2rem; margin: 16px 0 10px 0; }
        /* Reset DataFrame padding to fit on mobile */
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            padding: 8px !important;
            font-size: 0.8rem;
        }
    }

    /* ---- Modern Segmented Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border-radius: 12px;
        padding: 4px;
        gap: 8px;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px !important;
        color: #94a3b8 !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
        border: none !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0 !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(79, 139, 249, 0.15) !important;
        color: #4F8BF9 !important;
        border: 1px solid rgba(79, 139, 249, 0.3) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    /* Hide the active tab underline indicator */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* ---- KPI Cards (Glassmorphic Update) ---- */
    .kpi-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(79, 139, 249, 0.15);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(79, 139, 249, 0.25);
        border-color: rgba(79, 139, 249, 0.4);
    }
    .kpi-value {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
        text-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
    }
    .kpi-label {
        color: #cbd5e1;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-delta { font-size: 0.8rem; margin-top: 4px; font-weight: 500; }

    /* ---- Risk Badges ---- */
    .risk-high {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white; padding: 4px 14px; border-radius: 20px;
        font-weight: 600; font-size: 0.8rem;
        animation: pulse-red 2s infinite;
    }
    .risk-medium {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white; padding: 4px 14px; border-radius: 20px;
        font-weight: 600; font-size: 0.8rem;
    }
    .risk-low {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white; padding: 4px 14px; border-radius: 20px;
        font-weight: 600; font-size: 0.8rem;
    }

    /* ---- Section Headers ---- */
    .section-header {
        font-size: 1.4rem; font-weight: 600; color: #f8fafc;
        margin: 24px 0 16px 0; padding-bottom: 8px;
        border-bottom: 1px solid rgba(79, 139, 249, 0.2);
        display: inline-block;
    }

    /* ---- Intervention Card (Glassmorphic) ---- */
    .intervention-card {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(79, 139, 249, 0.15); 
        border-radius: 12px;
        padding: 20px; margin: 10px 0;
        border-left: 4px solid #4F8BF9;
        transition: all 0.3s ease;
    }
    .intervention-card:hover {
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(79, 139, 249, 0.4);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .intervention-card h4 { color: #f1f5f9; margin: 0 0 8px 0; font-weight: 600;}
    .intervention-card p  { color: #cbd5e1; font-size: 0.95rem; margin: 4px 0; line-height: 1.5;}
    .evidence-tag {
        background: rgba(79, 139, 249, 0.15); color: #60a5fa;
        padding: 4px 10px; border-radius: 6px;
        font-size: 0.75rem; display: inline-block; margin-top: 8px;
    }

    /* ---- Scheme Card ---- */
    .scheme-card {
        background: linear-gradient(135deg, #1e293b 0%, #1a2332 100%);
        border: 1px solid #334155; border-radius: 12px;
        padding: 20px; margin: 10px 0;
        border-left: 4px solid #10b981;
    }

    /* ---- Message Box ---- */
    .message-box {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 12px; padding: 20px;
        white-space: pre-wrap; color: #e2e8f0;
        font-size: 0.95rem; line-height: 1.6;
    }

    /* ---- Gauge ---- */
    .gauge-container { text-align: center; padding: 20px; }

    /* ---- Title styling ---- */
    .main-title {
        font-size: 1.8rem; font-weight: 700;
        background: linear-gradient(135deg, #4F8BF9 0%, #38bdf8 50%, #818cf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #64748b; font-size: 0.95rem; margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #1a2332 100%);
        border: 1px solid #334155; border-radius: 12px; padding: 16px;
    }

    /* ---- Keyframes ---- */
    @keyframes float {
        0%   { transform: translateY(0px); }
        50%  { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    @keyframes pulse-red {
        0%   { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70%  { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
</style>
""", unsafe_allow_html=True)



# ---- Load background animation ----
import streamlit.components.v1 as components

_bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "background.html")
with open(_bg_path, "r", encoding="utf-8") as _f:
    _bg_html_content = _f.read()

_bg_wrapper = f"""
<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-9999;pointer-events:none;overflow:hidden;">
{_bg_html_content}
</div>
"""
components.html(_bg_wrapper, height=0, scrolling=False)


# ===================================================================
# DATA LOADING & MODEL INIT (cached)
# ===================================================================
USER_ACCOUNTS = {
    "admin": {"password": "admin@123", "role": "admin"},
    "staff": {"password": "staff@123", "role": "staff"},
    "teacher": {"password": "teacher@123", "role": "staff"},
}


import random

def ensure_student_schema(students_df, csv_path):
    """Ensure required student columns exist; migrate file if needed."""
    required_defaults = {
        "state": "Tamil Nadu",
        "zone": "North Zone",
        "district": "Chennai",
        "location_type": "City",  # Added for city/village filter
        "phone": "+91-00000-00000",
        "address": "Address not available",
        "dropout_reason": "None reported",
    }
    changed = False
    for col, default_value in required_defaults.items():
        if col not in students_df.columns:
            if col == "location_type":
                # Randomly assign City or Village for realistic filtering
                students_df[col] = [random.choice(["City", "Village"]) for _ in range(len(students_df))]
            else:
                students_df[col] = default_value
            changed = True
        else:
            if col != "location_type":
                students_df[col] = students_df[col].fillna(default_value)

    if changed:
        students_df.to_csv(csv_path, index=False)
    return students_df


import sqlalchemy
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:2005@localhost:5432/safepath_db")

@st.cache_resource
def get_db_engine():
    return sqlalchemy.create_engine(DATABASE_URL)


@st.cache_data
def load_data():
    try:
        engine = get_db_engine()
        students = pd.read_sql("SELECT * FROM students", con=engine)
        interventions = pd.read_sql("SELECT * FROM interventions", con=engine)
        schemes = pd.read_sql("SELECT * FROM schemes", con=engine)
        return students, interventions, schemes
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


@st.cache_resource
def train_model():
    engine = get_db_engine()
    df = pd.read_sql("SELECT * FROM students", con=engine)
    if "location_type" not in df.columns:
        df["location_type"] = "City"
    model = DropoutRiskModel()
    accuracy = model.train(df)
    return model, accuracy


# Try loading
try:
    all_students_df, interventions_df, schemes_df = load_data()
    model, model_accuracy = train_model()
    if not all_students_df.empty:
        # Compute risk scores for all students
        all_students_df["risk_score"] = model.predict_batch(all_students_df)
        all_students_df["risk_level"] = all_students_df["risk_score"].apply(
            lambda x: "High" if x > 60 else ("Medium" if x > 35 else "Low")
        )
        all_students_df = model.identify_high_risk_students(all_students_df)
except Exception as e:
    st.error(f"⚠️ Error initializing app with database: {e}")
    st.stop()


# ===================================================================
# AUTH + QUERY-PARAM ROLE SWITCH + REGISTRATION
# ===================================================================
import json

base = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(base, "data", "users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {
        "admin": {"password": "admin", "role": "admin"},
        "staff": {"password": "staff", "role": "staff"},
        "teacher": {"password": "teacher", "role": "teacher"},
    }

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)

USER_ACCOUNTS = load_users()

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if "show_register" not in st.session_state:
    st.session_state.show_register = False

# Handle role switch from top navbar pills via query params
_qp = st.query_params
if "switch_role" in _qp and st.session_state.auth.get("logged_in"):
    _nr = _qp["switch_role"]
    if _nr in ("admin", "staff"):
        st.session_state.auth["role"] = _nr
        st.session_state.auth["username"] = _nr
    st.query_params.clear()
    st.rerun()

# ---- Login / Register page (shown when not authenticated) ----
if not st.session_state.auth["logged_in"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, auth_col, col3 = st.columns([1.2, 1, 1.2])
    with auth_col:
        st.markdown(
            '''<div style="text-align: center; margin-bottom: 2rem;">
                <span style="font-size: 3.5rem; font-weight: 700; background: linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);">SafePath AI</span><br>
                <span style="color: #94a3b8; font-size: 1.1rem; letter-spacing: 0.5px;">Student Dropout Early Warning System</span>
            </div>''',
            unsafe_allow_html=True
        )
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])
            
            with tab_login:
                st.markdown('<div class="main-subtitle" style="text-align:center;">Enter your credentials to continue</div>', unsafe_allow_html=True)
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sign In", width='stretch', type="primary", key="main_signin"):
                    acct = USER_ACCOUNTS.get(username.strip().lower())
                    if acct and password == acct["password"]:
                        st.session_state.auth = {
                            "logged_in": True,
                            "username": username.strip().lower(),
                            "role": acct["role"],
                        }
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        
                st.markdown("<br>", unsafe_allow_html=True)
                
                
            with tab_register:
                st.markdown('<div class="main-subtitle" style="text-align:center;">Create a new account</div>', unsafe_allow_html=True)
                new_user = st.text_input("New Username", key="reg_user").strip().lower()
                new_pass = st.text_input("New Password", type="password", key="reg_pass")
                new_role = st.selectbox("Select Role", ["staff", "teacher", "admin"], key="reg_role")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Account", width='stretch', type="primary", key="main_register"):
                    if not new_user or not new_pass:
                        st.error("Please fill in all fields.")
                    elif new_user in USER_ACCOUNTS:
                        st.error("Username already exists. Please choose a different one.")
                    else:
                        USER_ACCOUNTS[new_user] = {"password": new_pass, "role": new_role}
                        save_users(USER_ACCOUNTS)
                        st.success(f"Account '{new_user}' created successfully! You can now switch to the **Sign In** tab.")
    st.stop()

# ---- Top Navbar (only when logged in) ----
_auth = st.session_state.auth
_cur_role = _auth["role"]
_admin_active  = 'role-pill role-pill-active'  if _cur_role == 'admin' else 'role-pill role-pill-inactive'
_staff_active  = 'role-pill role-pill-active'  if _cur_role == 'staff' else 'role-pill role-pill-inactive'
st.markdown(f"""
<div id="custom-topnav">
    <button id="sidebar-toggle" type="button" title="Toggle menu">&#9776;</button>
    <span id="topnav-logo">🔮 SafePath AI</span>
    <div id="topnav-right">
        <span class="topnav-user">👤 {_auth['username']}</span>
        <a href="?switch_role=admin" target="_self" class="{_admin_active}">Admin</a>
        <a href="?switch_role=staff" target="_self" class="{_staff_active}">Staff</a>
        <a href="?logout=1" target="_self" class="topnav-logout" id="logout-btn">⏻ Logout</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle logout query param
if "logout" in _qp:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.query_params.clear()
    st.rerun()

# ===================================================================
# SIDEBAR NAVIGATION (left menu)
# ===================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 18px 0;">
        <div style="font-size: 2.2rem;">🔮</div>
        <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-top: 4px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);">SafePath AI</div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">Student Dropout Risk System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    user_role = st.session_state.auth["role"]

    if user_role == "admin":
        page = st.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "🎯 Student Risk Analysis",
                "📋 Intervention Playbook",
                "💬 Parent Communication",
                "🏛️ Government Schemes",
                "🗺️ District Heatmap",
                "📈 Intervention Tracker",
                "🤖 AI Chatbot",
            ],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "Navigation",
            [
                "📝 Student Data Entry",
                "🎯 Student Risk Analysis",
                "📋 Intervention Playbook",
                "💬 Parent Communication",
                "🤖 AI Chatbot",
            ],
            label_visibility="collapsed",
        )

    st.markdown("---")

    # ---- Cascading filters: Zone → District → City/Village → School ----
    if user_role == "admin":
        zone_options = ["All"] + sorted(all_students_df["zone"].dropna().unique().tolist())
        selected_zone = st.selectbox("Zone", zone_options, index=0)
        filtered_df = all_students_df if selected_zone == "All" else all_students_df[all_students_df["zone"] == selected_zone]
    else:
        zone_options = sorted(all_students_df["zone"].dropna().unique().tolist())
        if "staff_zone" not in st.session_state:
            st.session_state.staff_zone = zone_options[0]
        selected_zone = st.selectbox("Your Zone", zone_options, index=zone_options.index(st.session_state.staff_zone) if st.session_state.staff_zone in zone_options else 0)
        st.session_state.staff_zone = selected_zone
        filtered_df = all_students_df[all_students_df["zone"] == selected_zone]

    district_options_list = sorted(filtered_df["district"].dropna().unique().tolist())
    if user_role == "admin":
        district_options = ["All"] + district_options_list
        selected_district = st.selectbox("District", district_options, index=0)
        filtered_df = filtered_df if selected_district == "All" else filtered_df[filtered_df["district"] == selected_district]
    else:
        if "staff_district" not in st.session_state:
            st.session_state.staff_district = district_options_list[0] if district_options_list else ""
        selected_district = st.selectbox("Your District", district_options_list, index=district_options_list.index(st.session_state.staff_district) if st.session_state.staff_district in district_options_list else 0)
        st.session_state.staff_district = selected_district
        filtered_df = filtered_df[filtered_df["district"] == selected_district]

    if user_role == "admin":
        loc_options = ["All", "City", "Village"]
        selected_loc = st.selectbox("City / Village", loc_options, index=0)
        filtered_df = filtered_df if selected_loc == "All" else filtered_df[filtered_df["location_type"] == selected_loc]

    school_options_list = sorted(filtered_df["school"].dropna().unique().tolist())
    if user_role == "admin":
        school_options = ["All"] + school_options_list
        selected_school = st.selectbox("School", school_options, index=0)
        students_df = filtered_df if selected_school == "All" else filtered_df[filtered_df["school"] == selected_school]
    else:
        selected_school = st.selectbox("Your School", school_options_list, index=0) if school_options_list else ""
        students_df = filtered_df[filtered_df["school"] == selected_school] if selected_school else filtered_df

    st.markdown("---")

    st.markdown(f"""
    <div style="padding: 12px; background: #0f1724; border-radius: 10px;
                border: 1px solid #1e3a5f; margin-top: 10px;">
        <div style="color: #60a5fa; font-size: 0.75rem; font-weight: 600;">MODEL STATUS</div>
        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 6px;">
            ✅ Trained — {model_accuracy:.1%} accuracy
        </div>
        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">
            📊 {len(students_df)} students in view
        </div>
        <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">
            🕐 {datetime.now().strftime('%d %b %Y, %I:%M %p')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Sidebar open/close toggle button at bottom ----
    st.markdown("""
    <div style="margin-top: 20px; text-align: center;">
        <button id="close-menu-btn" type="button"
            style="background:rgba(79,139,249,0.08); border:1px solid rgba(79,139,249,0.25);
                   color:#64748b; border-radius:8px; padding:6px 20px; cursor:pointer; font-size:0.78rem;">
            ← Close Menu
        </button>
    </div>
    """, unsafe_allow_html=True)

    # Inject sidebar toggle Javascript
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (() => {
        const getParentDoc = () => {
            try {
                return window.parent && window.parent.document ? window.parent.document : document;
            } catch (e) {
                return document;
            }
        };

        const toggleSidebar = () => {
            const p = getParentDoc();
            const selectors = [
                "[data-testid='stSidebarCollapsedControl'] button",
                ".stSidebarCollapsedControl button",
                "[data-testid='stSidebarCollapseButton']",
                "[data-testid='collapsedControl']",
                "button[aria-label*='sidebar' i]",
                "button[title*='sidebar' i]"
            ];

            for (const sel of selectors) {
                const el = p.querySelector(sel);
                if (el) {
                    el.click();
                    return;
                }
            }
        };

        // We use setInterval to ensure it attaches to dynamically rendered elements
        const attachHandlers = () => {
            const doc = getParentDoc();
            const btnTop = doc.getElementById("sidebar-toggle");
            if (btnTop && !btnTop.hasAttribute("data-sidebar-attached")) {
                btnTop.addEventListener("click", toggleSidebar);
                btnTop.setAttribute("data-sidebar-attached", "true");
            }
            const btnClose = doc.getElementById("close-menu-btn");
            if (btnClose && !btnClose.hasAttribute("data-sidebar-attached")) {
                btnClose.addEventListener("click", toggleSidebar);
                btnClose.setAttribute("data-sidebar-attached", "true");
            }
        };
        
        setInterval(attachHandlers, 1000);
        attachHandlers();
    })();
    </script>
    """, height=0, width=0)


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================
def risk_badge(level):
    cls = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}.get(level, "risk-low")
    return f'<span class="{cls}">{level} Risk</span>'


def kpi_card(label, value, delta=None, icon=""):
    delta_html = ""
    if delta:
        try:
            # Extract numeric part from delta string
            num_str = ''.join(c for c in str(delta) if c in '0123456789.-+')
            is_positive = float(num_str) > 0 if num_str else True
        except (ValueError, TypeError):
            is_positive = True
        color = "#10b981" if is_positive else "#ef4444"
        delta_html = f'<div class="kpi-delta" style="color:{color};">{delta}</div>'
    return f"""
    <div class="kpi-card">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """


# Handle empty filtered views gracefully.
if students_df.empty:
    st.warning("No students found for the selected State/District/School filters.")
    st.stop()


# ===================================================================
# PAGE 1: DASHBOARD
# ===================================================================
if page == "📊 Dashboard":
    st.markdown('<div class="main-title">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Real-time overview of student dropout risk across your institution</div>', unsafe_allow_html=True)

    # KPI Row
    total = len(students_df)
    high_risk = len(students_df[students_df["risk_level"] == "High"])
    medium_risk = len(students_df[students_df["risk_level"] == "Medium"])
    avg_attendance = round(students_df["attendance"].mean(), 1)

    # Intervention success rate
    if not interventions_df.empty:
        improved = sum(interventions_df["attendance_after"] > interventions_df["attendance_before"])
        success_rate = round(improved / len(interventions_df) * 100, 1)
    else:
        success_rate = 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Students", total, icon="👥"), unsafe_allow_html=True)
    with c2:
        high_risk_pct = round(high_risk / total * 100, 1) if total else 0
        st.markdown(kpi_card("High Risk", high_risk, f"{high_risk_pct}% of total", icon="🚨"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Avg Attendance", f"{avg_attendance}%", icon="📅"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Intervention Success", f"{success_rate}%", icon="✅"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Risk Distribution</div>', unsafe_allow_html=True)
        risk_counts = students_df["risk_level"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            color=risk_counts.index,
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
            hole=0.55,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            showlegend=True,
            height=350,
            margin=dict(t=20, b=20, l=20, r=20),
        )
        fig.update_traces(textinfo="percent+value", textfont_size=13)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown('<div class="section-header">Risk Score Distribution</div>', unsafe_allow_html=True)
        fig2 = px.histogram(
            students_df,
            x="risk_score",
            nbins=20,
            color_discrete_sequence=["#4F8BF9"],
            labels={"risk_score": "Risk Score"},
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            xaxis_title="Risk Score",
            yaxis_title="Number of Students",
            height=350,
            margin=dict(t=20, b=40, l=40, r=20),
        )
        fig2.update_xaxes(gridcolor="#1e293b")
        fig2.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig2, width='stretch')

    # Bottom Row
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Attendance vs Math Score</div>', unsafe_allow_html=True)
        fig3 = px.scatter(
            students_df,
            x="attendance",
            y="math_score",
            color="risk_level",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
            opacity=0.7,
            labels={"attendance": "Attendance %", "math_score": "Math Score"},
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            height=350,
            margin=dict(t=20, b=40, l=40, r=20),
        )
        fig3.update_xaxes(gridcolor="#1e293b")
        fig3.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig3, width='stretch')

    with col4:
        st.markdown('<div class="section-header">Risk by Class</div>', unsafe_allow_html=True)
        class_risk = students_df.groupby(["class", "risk_level"]).size().reset_index(name="count")
        fig4 = px.bar(
            class_risk,
            x="class",
            y="count",
            color="risk_level",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"},
            barmode="stack",
            labels={"class": "Class", "count": "Students"},
        )
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            height=350,
            margin=dict(t=20, b=40, l=40, r=20),
        )
        fig4.update_xaxes(gridcolor="#1e293b")
        fig4.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig4, width='stretch')

    # High Risk Students Table
    st.markdown('<div class="section-header">🚨 High Risk Students</div>', unsafe_allow_html=True)
    with st.container(border=True):
        high_risk_df = students_df[students_df["high_risk_flag"]].sort_values("risk_priority", ascending=False).copy()
        high_risk_df["phone_link"] = high_risk_df["phone"].apply(lambda p: f"tel:{p}")
        display_cols = ["student_id", "name", "class", "district", "school", "phone_link", "attendance", "math_score", "risk_score", "risk_priority", "risk_level"]
        
        # Action Bar above table
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f"Showing all {len(high_risk_df)} high-risk students in view.")
        with c2:
            st.download_button(
                label="📥 Export to CSV",
                data=high_risk_df[display_cols].to_csv(index=False).encode('utf-8'),
                file_name=f"high_risk_students_{selected_zone}_{selected_district}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        st.dataframe(
            high_risk_df[display_cols],  # Removed .head(15) restriction
            width='stretch',
            hide_index=True,
            column_config={
                "student_id": "ID",
                "name": "Name",
                "class": "Class",
                "district": "District",
                "school": "School",
                "phone_link": st.column_config.LinkColumn("Phone", display_text="📞 Call"),
                "attendance": st.column_config.ProgressColumn("Attendance", min_value=0, max_value=100, format="%d%%"),
                "math_score": st.column_config.ProgressColumn("Math Score", min_value=0, max_value=100, format="%d"),
                "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%.1f"),
                "risk_priority": st.column_config.ProgressColumn("Priority Score", min_value=0, max_value=100, format="%.1f"),
                "risk_level": "Risk Level",
            },
        )


# ===================================================================
# PAGE 2: STUDENT RISK ANALYSIS
# ===================================================================
elif page == "🎯 Student Risk Analysis":
    st.markdown('<div class="main-title">🎯 Student Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Detailed dropout risk assessment with explainable AI factors</div>', unsafe_allow_html=True)

    # Student selector
    col_search, col_filter = st.columns([3, 1])
    working_df = students_df.copy()
    with col_search:
        filter_risk = st.selectbox("Filter by Risk", ["All", "High", "Medium", "Low"])
        if filter_risk != "All":
            working_df = working_df[working_df["risk_level"] == filter_risk]
    with col_filter:
        student_options = [
            f"{row['student_id']} — {row['name']} (Class {row['class']}{row['section']})"
            for _, row in working_df.iterrows()
        ]
        if not student_options:
            st.info("No students found for the selected risk filter.")
            st.stop()
        selected = st.selectbox("Select Student", student_options, index=0)

    selected_id = int(selected.split(" — ")[0])
    student = working_df[working_df["student_id"] == selected_id].iloc[0]
    student_dict = student.to_dict()

    risk_score = student["risk_score"]
    risk_level = student["risk_level"]

    # Top row: Risk gauge + Student info
    col_gauge, col_info = st.columns([1, 2])

    with col_gauge:
        # Risk Gauge using Plotly
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            number={"suffix": "%", "font": {"size": 42, "color": "#e2e8f0"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569"},
                "bar": {"color": "#ef4444" if risk_score > 60 else ("#f59e0b" if risk_score > 35 else "#10b981")},
                "bgcolor": "#1e293b",
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 35], "color": "#064e3b"},
                    {"range": [35, 60], "color": "#78350f"},
                    {"range": [60, 100], "color": "#7f1d1d"},
                ],
                "threshold": {
                    "line": {"color": "#f8fafc", "width": 3},
                    "thickness": 0.8,
                    "value": risk_score,
                },
            },
            title={"text": "Dropout Risk Score", "font": {"size": 16, "color": "#94a3b8"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            height=280,
            margin=dict(t=50, b=20, l=30, r=30),
        )
        st.plotly_chart(fig_gauge, width='stretch')

    with col_info:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #1a2332); border: 1px solid #334155;
                    border-radius: 16px; padding: 24px; margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="color: #e2e8f0; margin: 0;">{student['name']}</h3>
                {risk_badge(risk_level)}
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">CLASS</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['class']}{student['section']}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">GENDER</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['gender']}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">ATTENDANCE</div>
                    <div style="color: {'#ef4444' if student['attendance'] < 60 else '#10b981'}; font-weight: 600;">{student['attendance']}%</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">DISTANCE</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['distance_km']} km</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">FAMILY INCOME</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['family_income'].title()}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">SIBLING DROPOUT</div>
                    <div style="color: {'#ef4444' if student['sibling_dropout'] == 'yes' else '#10b981'}; font-weight: 600;">{student['sibling_dropout'].title()}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">PHONE</div>
                    <div style="color: #60a5fa; font-weight: 600;"><a href="tel:{student['phone']}" style="color:#60a5fa;text-decoration:none;">{student['phone']}</a></div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">DISTRICT / STATE</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['district']}, {student['state']}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.75rem;">DROPOUT REASON</div>
                    <div style="color: #e2e8f0; font-weight: 600;">{student['dropout_reason']}</div>
                </div>
            </div>
            <div style="margin-top: 12px;">
                <div style="color: #64748b; font-size: 0.75rem;">ADDRESS</div>
                <div style="color: #e2e8f0; font-weight: 600;">{student['address']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------
    # ADVANCED HACKATHON FEATURES: What-If Simulator & Scheme Matcher
    # -----------------------------------------------------------
    col_sim, col_schemes = st.columns(2)

    with col_sim:
        st.markdown('<div class="section-header">⚙️ Predictive "What-If" Simulator</div>', unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Move the sliders to see how improving attendance and scores affects the AI risk prediction.</p>", unsafe_allow_html=True)
        
        sim_attendance = st.slider("Simulated Attendance (%)", min_value=0, max_value=100, value=int(student['attendance']))
        sim_math = st.slider("Simulated Math Score", min_value=0, max_value=100, value=int(student['math_score']))
        sim_engagement = st.slider("Simulated Engagement", min_value=0, max_value=100, value=int(student['engagement_score']))
        
        # Run prediction on simulated data
        sim_student = student_dict.copy()
        sim_student["attendance"] = sim_attendance
        sim_student["math_score"] = sim_math
        sim_student["engagement_score"] = sim_engagement
        
        sim_risk = model.predict_batch(pd.DataFrame([sim_student]))[0]
        risk_diff = round(sim_risk - risk_score, 1)
        
        st.metric(
            label="Simulated Risk Score", 
            value=f"{sim_risk}%", 
            delta=f"{risk_diff}%" if risk_diff != 0 else "No Change", 
            delta_color="inverse"
        )
        if sim_risk < 35 and risk_score >= 35:
            st.success("✨ This intervention would move the student to LOW risk!")

    with col_schemes:
        st.markdown('<div class="section-header">🏛️ Auto-Matched Schemes</div>', unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>AI cross-referenced this student's profile against government schemes.</p>", unsafe_allow_html=True)
        
        # Simple logical matcher based on scheme attributes
        matched_schemes = []
        for _, scheme in schemes_df.iterrows():
            match = True
            
            # Distance logic
            if scheme['eligibility_distance'] > 0 and student['distance_km'] < scheme['eligibility_distance']:
                match = False
                
            # Income logic
            if scheme['eligibility_income'] == 'low' and student['family_income'] != 'low':
                match = False
                
            # Gender logic (implicit in some scheme names)
            if "Girl" in scheme['scheme_name'] and student['gender'] != 'Female':
                match = False
                
            if match:
                matched_schemes.append(scheme)
                
        if matched_schemes:
            for s in matched_schemes[:3]: # Show top 3 matches
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; padding: 10px; margin-bottom: 8px; border-radius: 4px;">
                    <div style="color: #e2e8f0; font-weight: bold; font-size: 0.95rem;">{s['scheme_name']}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">{s['benefit']}</div>
                </div>
                """, unsafe_allow_html=True)
            if len(matched_schemes) > 3:
                st.markdown(f"<p style='color: #60a5fa; font-size: 0.85rem;'>+ {len(matched_schemes) - 3} more schemes match.</p>", unsafe_allow_html=True)
                
            st.button("✉️ SMS Parent Application Details", key=f"sms_{student['student_id']}", help="Feature demo: This would send an SMS to the parent's phone.")
        else:
            st.info("No specifically matched conditional schemes found (only general universal schemes apply).")

    st.markdown("<br>", unsafe_allow_html=True)

    role = st.session_state.auth["role"]
    st.markdown('<div class="section-header">🧾 Student Profile Access</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if role == "admin":
            st.info("Admin view is read-only. Staff/teacher accounts can edit student details.")
            st.dataframe(
                pd.DataFrame([{
                    "Phone": student["phone"],
                    "Address": student["address"],
                    "Dropout Reason": student["dropout_reason"],
                    "Attendance": student["attendance"],
                    "Engagement": student["engagement_score"],
                }]),
                width='stretch',
                hide_index=True,
            )
        else:
            with st.form("edit_student_details"):
                e1, e2 = st.columns(2)
                with e1:
                    edited_phone = st.text_input("Phone", value=str(student["phone"]))
                    edited_reason = st.text_input("Dropout Reason", value=str(student["dropout_reason"]))
                    edited_attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, value=int(student["attendance"]))
                with e2:
                    edited_address = st.text_area("Address", value=str(student["address"]), height=70)
                    edited_engagement = st.number_input("Engagement Score", min_value=0, max_value=100, value=int(student["engagement_score"]))
                    edited_distance = st.number_input("Distance (km)", min_value=0.0, max_value=30.0, value=float(student["distance_km"]), step=0.1)

                if st.form_submit_button("Save Student Updates", type="primary", width='stretch'):
                    csv_path = os.path.join(base, "data", "students.csv")
                    source_df = pd.read_csv(csv_path)
                    source_df = ensure_student_schema(source_df, csv_path)
                    idx = source_df[source_df["student_id"] == selected_id].index
                    if len(idx) == 1:
                        row_idx = idx[0]
                        source_df.loc[row_idx, "phone"] = edited_phone.strip()
                        source_df.loc[row_idx, "address"] = edited_address.strip()
                        source_df.loc[row_idx, "dropout_reason"] = edited_reason.strip() or "None reported"
                        source_df.loc[row_idx, "attendance"] = int(edited_attendance)
                        source_df.loc[row_idx, "engagement_score"] = int(edited_engagement)
                        source_df.loc[row_idx, "distance_km"] = float(edited_distance)
                        source_df.to_csv(csv_path, index=False)
                        st.cache_data.clear()
                        st.cache_resource.clear()
                        st.success("Student record updated successfully.")
                        st.rerun()
                    else:
                        st.error("Unable to uniquely locate this student in the source dataset.")

    # Top 3 Contributing Factors
    col_factors, col_cohort = st.columns(2)

    with col_factors:
        st.markdown('<div class="section-header">🔍 Top Contributing Factors</div>', unsafe_allow_html=True)
        with st.container(border=True):
            top_factors = model.get_top_factors(student_dict, top_n=3)

            for i, factor in enumerate(top_factors, 1):
                icon = "⚠️" if factor["is_risk_factor"] else "✅"
                color = "#ef4444" if factor["is_risk_factor"] else "#10b981"
                bg_color = "rgba(15, 23, 42, 0.4)"
                st.markdown(f"""
                <div style="background: {bg_color}; border-radius: 12px; padding: 16px; margin: 8px 0;
                            border-left: 4px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.1rem;">{icon}</span>
                            <span style="color: #e2e8f0; font-weight: 600; margin-left: 8px;">
                                #{i} {factor['description']}
                            </span>
                        </div>
                        <div style="color: {color}; font-weight: 600; font-size: 0.85rem;">
                            {factor['direction']}
                        </div>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px; margin-left: 32px;">
                        {factor['label']}: <strong>{factor['value']}</strong> | Model importance: {factor['importance']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_cohort:
        st.markdown('<div class="section-header">📊 Cohort Comparison</div>', unsafe_allow_html=True)
        with st.container(border=True):
            comparison = model.get_cohort_comparison(student_dict, students_df)

            comp_df = pd.DataFrame(comparison)
            fig_comp = go.Figure()

            fig_comp.add_trace(go.Bar(
                name="Student",
                x=comp_df["indicator"],
                y=comp_df["student_value"],
                marker_color="#4F8BF9",
            ))
            fig_comp.add_trace(go.Bar(
                name="Class Average",
                x=comp_df["indicator"],
                y=comp_df["class_average"],
                marker_color="#64748b",
            ))
            fig_comp.add_trace(go.Bar(
                name="Successful Students",
                x=comp_df["indicator"],
                y=comp_df["successful_average"],
                marker_color="#10b981",
            ))

            fig_comp.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=320,
                margin=dict(t=20, b=40, l=40, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )
            fig_comp.update_xaxes(gridcolor="#1e293b", tickangle=-30)
            fig_comp.update_yaxes(gridcolor="#1e293b")
            st.plotly_chart(fig_comp, width='stretch')


# ===================================================================
# PAGE 3: INTERVENTION PLAYBOOK
# ===================================================================
elif page == "📋 Intervention Playbook":
    st.markdown('<div class="main-title">📋 Intervention Playbook</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Evidence-based intervention recommendations ranked by student risk profile</div>', unsafe_allow_html=True)

    # Student selector
    student_options = [
        f"{row['student_id']} — {row['name']} (Risk: {row['risk_score']}%)"
        for _, row in students_df.sort_values("risk_score", ascending=False).iterrows()
    ]
    selected = st.selectbox("Select Student", student_options, index=0)
    selected_id = int(selected.split(" — ")[0])
    student = students_df[students_df["student_id"] == selected_id].iloc[0]
    student_dict = student.to_dict()

    risk_score = student["risk_score"]
    st.markdown(f"**{student['name']}** — Class {student['class']}{student['section']} — "
                f"Risk Score: **{risk_score}%** {risk_badge(student['risk_level'])}", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    recommendations = recommend_interventions(student_dict, top_n=6)

    if not recommendations:
        st.success("✅ This student has no significant risk factors. No interventions needed at this time.")
    else:
        for i, rec in enumerate(recommendations, 1):
            success_color = "#10b981" if rec["success_rate"] >= 0.7 else ("#f59e0b" if rec["success_rate"] >= 0.6 else "#94a3b8")
            st.markdown(f"""
            <div class="intervention-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4>#{i} {rec['name']}</h4>
                        <p>{rec['description']}</p>
                    </div>
                    <div style="text-align: right; min-width: 120px;">
                        <div style="color: {success_color}; font-size: 1.5rem; font-weight: 700;">
                            {round(rec['success_rate'] * 100)}%
                        </div>
                        <div style="color: #64748b; font-size: 0.7rem;">SUCCESS RATE</div>
                    </div>
                </div>
                <div style="margin-top: 8px;">
                    <span style="color: #64748b; font-size: 0.8rem;">Matching factors:</span>
                    {''.join(f'<span style="background:#1e3a5f; color:#60a5fa; padding:2px 8px; border-radius:4px; font-size:0.75rem; margin-left:4px;">{t}</span>' for t in rec['matching_triggers'])}
                </div>
                <div class="evidence-tag">📚 {rec['evidence']}</div>
            </div>
            """, unsafe_allow_html=True)


# ===================================================================
# PAGE 4: PARENT COMMUNICATION
# ===================================================================
elif page == "💬 Parent Communication":
    st.markdown('<div class="main-title">💬 Parent Communication Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Auto-draft sensitive, stigma-free messages for parents in English and Tamil</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        student_options = [
            f"{row['student_id']} — {row['name']}"
            for _, row in students_df.iterrows()
        ]
        selected = st.selectbox("Select Student", student_options, index=0)
        selected_id = int(selected.split(" — ")[0])
        student = students_df[students_df["student_id"] == selected_id].iloc[0]

    with col2:
        language = st.selectbox("Language", ["English", "Tamil"])
        msg_type = st.selectbox("Message Type", ["Formal Letter", "WhatsApp Message"])

    # Auto-detect concerns
    concerns = []
    if student["attendance"] < 70:
        concerns.append("attendance")
    if student["math_score"] < 50 or student.get("science_score", 100) < 50:
        concerns.append("academics")
    if student.get("engagement_score", 100) < 55:
        concerns.append("engagement")
    if student["distance_km"] > 5:
        concerns.append("distance")
    if student["family_income"] == "low":
        concerns.append("economic")

    if not concerns:
        concerns = ["attendance"]

    st.markdown("**Detected Concerns:**")
    selected_concerns = st.multiselect(
        "Customize concerns to address",
        ["attendance", "academics", "engagement", "distance", "economic"],
        default=concerns,
    )

    if st.button("📝 Generate Message", type="primary", width='stretch'):
        lang = "tamil" if language == "Tamil" else "english"

        if msg_type == "Formal Letter":
            message = generate_parent_message(student["name"], lang, selected_concerns)
        else:
            message = generate_whatsapp_message(student["name"], lang, selected_concerns)

        st.markdown('<div class="section-header">Generated Message</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="message-box">{message}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.code(message, language=None)
        st.caption("💡 Copy the message above and send via WhatsApp, SMS, or print as a letter.")

    # Sensitivity guardrails note
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "🛡️ **Sensitivity Guardrails Active**\n\n"
        "Messages never contain words like _dropout_, _failing_, _at risk_, or _poor performance_. "
        "All communication uses encouraging, supportive language focused on partnership between school and family."
    )


# ===================================================================
# PAGE 5: GOVERNMENT SCHEMES
# ===================================================================
elif page == "🏛️ Government Schemes":
    st.markdown('<div class="main-title">🏛️ Government Scheme Matcher</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Identify eligible central and state government schemes with application checklists</div>', unsafe_allow_html=True)

    # Summary
    summary = get_scheme_summary(schemes_df)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi_card("Total Active Schemes", summary.get("total_schemes", 0), icon="📋"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Central Schemes", summary.get("central_schemes", 0), icon="🇮🇳"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("State Schemes", summary.get("state_schemes", 0), icon="🏛️"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Student selector for eligibility check
    student_options = [
        f"{row['student_id']} — {row['name']} (Income: {row['family_income']}, Dist: {row['distance_km']}km)"
        for _, row in students_df.iterrows()
    ]
    selected = st.selectbox("Check Eligibility for Student", student_options, index=0)
    selected_id = int(selected.split(" — ")[0])
    student = students_df[students_df["student_id"] == selected_id].iloc[0]

    if st.button("🔍 Check Eligibility", type="primary", width='stretch'):
        matched = match_schemes(student, schemes_df)

        if not matched:
            st.warning("No matching schemes found for this student's profile.")
        else:
            st.success(f"✅ Found **{len(matched)}** eligible schemes for **{student['name']}**")

            for scheme in matched:
                docs_html = "".join(
                    f'<div style="color: #94a3b8; font-size: 0.85rem; padding: 4px 0;">'
                    f'☐ {item["document"]}</div>'
                    for item in scheme["checklist"]
                )

                st.markdown(f"""
                <div class="scheme-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="color: #e2e8f0; margin: 0 0 8px 0;">{scheme['scheme_name']}</h4>
                            <span style="background: {'#1e3a5f' if scheme['type'] == 'Central' else '#1a3a2f'};
                                         color: {'#60a5fa' if scheme['type'] == 'Central' else '#10b981'};
                                         padding: 2px 10px; border-radius: 6px; font-size: 0.75rem;">
                                {scheme['type']}
                            </span>
                        </div>
                    </div>
                    <p style="color: #94a3b8; margin: 12px 0 8px 0;">
                        <strong style="color: #e2e8f0;">Benefit:</strong> {scheme['benefit']}
                    </p>
                    <div style="margin-top: 12px;">
                        <div style="color: #e2e8f0; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">
                            📋 Application Checklist:
                        </div>
                        {docs_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ===================================================================
# PAGE 6: DISTRICT HEATMAP
# ===================================================================
elif page == "🗺️ District Heatmap":
    st.markdown('<div class="main-title">🗺️ District Dropout Risk Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Aggregated school-level risk view for district education officers</div>', unsafe_allow_html=True)

    # Aggregate by school
    school_stats = students_df.groupby("school").agg(
        total_students=("student_id", "count"),
        high_risk=("risk_level", lambda x: (x == "High").sum()),
        medium_risk=("risk_level", lambda x: (x == "Medium").sum()),
        avg_risk_score=("risk_score", "mean"),
        avg_attendance=("attendance", "mean"),
        avg_math=("math_score", "mean"),
    ).reset_index()

    school_stats["risk_pct"] = round(school_stats["high_risk"] / school_stats["total_students"] * 100, 1)
    school_stats["school_short"] = school_stats["school"].apply(lambda x: x.split(" - ")[-1] if " - " in x else x)
    school_stats = school_stats.sort_values("high_risk", ascending=False)

    # Heatmap & Geographical Map
    st.markdown('<div class="section-header">🌍 State-wide Risk Map & Concentration</div>', unsafe_allow_html=True)
    
    # Static coordinates for TN Districts
    TN_DISTRICT_COORDS = {
        "Chennai": (13.0827, 80.2707),
        "Kancheepuram": (12.8342, 79.7036),
        "Tiruvallur": (13.1436, 79.9126),
        "Vellore": (12.9165, 79.1325),
        "Madurai": (9.9252, 78.1198),
        "Tirunelveli": (8.7139, 77.7567),
        "Kanyakumari": (8.0883, 77.5385),
        "Thoothukudi": (8.7642, 78.1348),
        "Coimbatore": (11.0168, 76.9558),
        "Tiruppur": (11.1085, 77.3411),
        "Erode": (11.3410, 77.7172),
        "Salem": (11.6643, 78.1460),
        "Tiruchirappalli": (10.7905, 78.7047),
        "Thanjavur": (10.7870, 79.1378),
        "Karur": (10.9601, 78.0766),
        "Pudukkottai": (10.3833, 78.8001),
        "Cuddalore": (11.7480, 79.7714),
        "Viluppuram": (11.9401, 79.4861),
        "Tiruvannamalai": (12.2253, 79.0747),
        "Nagapattinam": (10.7656, 79.8424),
        "Ariyalur": (11.1401, 79.0786),
    }

    dist_stats = students_df.groupby("district").agg(
        total_students=("student_id", "count"),
        high_risk=("risk_level", lambda x: (x == "High").sum()),
        avg_risk_score=("risk_score", "mean"),
    ).reset_index()
    
    dist_stats["lat"] = dist_stats["district"].map(lambda x: TN_DISTRICT_COORDS.get(x, (11.1271, 78.6569))[0])
    dist_stats["lon"] = dist_stats["district"].map(lambda x: TN_DISTRICT_COORDS.get(x, (11.1271, 78.6569))[1])

    fig_map = px.scatter_mapbox(
        dist_stats,
        lat="lat",
        lon="lon",
        size="total_students",
        color="avg_risk_score",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        size_max=35,
        zoom=5.5,
        center={"lat": 11.1271, "lon": 78.6569},
        hover_name="district",
        hover_data={"total_students": True, "high_risk": True, "avg_risk_score": ":.1f", "lat": False, "lon": False},
        mapbox_style="carto-darkmatter"
    )
    fig_map.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0})
    
    col_map, col_tree = st.columns(2)
    with col_map:
        with st.container(border=True):
            st.plotly_chart(fig_map, width='stretch')
    
    with col_tree:
        with st.container(border=True):
            fig_heat = px.treemap(
                school_stats,
                path=["school_short"],
                values="total_students",
                color="avg_risk_score",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                hover_data=["total_students", "high_risk", "avg_attendance"],
            )
            fig_heat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=450,
                margin=dict(t=0, b=0, l=0, r=0),
                coloraxis_colorbar_title="Avg Risk",
            )
            st.plotly_chart(fig_heat, width='stretch')

    # Bar chart
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">High Risk Students by School</div>', unsafe_allow_html=True)
        with st.container(border=True):
            fig_bar = px.bar(
                school_stats,
                x="school_short",
                y=["high_risk", "medium_risk"],
                barmode="stack",
                color_discrete_sequence=["#ef4444", "#f59e0b"],
                labels={"value": "Students", "school_short": "School"},
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=350,
                margin=dict(t=20, b=60, l=40, r=20),
                legend_title="Risk Level",
            )
            fig_bar.update_xaxes(gridcolor="#1e293b", tickangle=-45)
            fig_bar.update_yaxes(gridcolor="#1e293b")
            st.plotly_chart(fig_bar, width='stretch')

    with col2:
        st.markdown('<div class="section-header">Average Attendance by School</div>', unsafe_allow_html=True)
        with st.container(border=True):
            fig_att = px.bar(
                school_stats.sort_values("avg_attendance"),
                x="school_short",
                y="avg_attendance",
                color="avg_attendance",
                color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                labels={"avg_attendance": "Avg Attendance %", "school_short": "School"},
            )
            fig_att.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=350,
                margin=dict(t=20, b=60, l=40, r=20),
            )
            fig_att.update_xaxes(gridcolor="#1e293b", tickangle=-45)
            fig_att.update_yaxes(gridcolor="#1e293b")
            st.plotly_chart(fig_att, width='stretch')

    # Detailed table
    st.markdown('<div class="section-header">📊 Detailed School Statistics</div>', unsafe_allow_html=True)
    with st.container(border=True):
        display_stats = school_stats[["school_short", "total_students", "high_risk", "medium_risk", "risk_pct", "avg_attendance", "avg_math"]].copy()
        display_stats.columns = ["School", "Total Students", "High Risk", "Medium Risk", "Risk %", "Avg Attendance", "Avg Math"]
        display_stats["Avg Attendance"] = display_stats["Avg Attendance"].round(1)
        display_stats["Avg Math"] = display_stats["Avg Math"].round(1)

        st.dataframe(display_stats, width='stretch', hide_index=True)


# ===================================================================
# PAGE 7: INTERVENTION TRACKER
# ===================================================================
elif page == "📈 Intervention Tracker":
    st.markdown('<div class="main-title">📈 Intervention Outcome Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Track 30-day outcomes of interventions and build an evidence base</div>', unsafe_allow_html=True)

    # Effectiveness summary
    effectiveness = get_intervention_effectiveness(interventions_df)

    if not effectiveness.empty:
        st.markdown('<div class="section-header">📊 Intervention Effectiveness Summary</div>', unsafe_allow_html=True)
        st.dataframe(effectiveness, width='stretch', hide_index=True)

        # Effectiveness chart
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">Attendance Change by Intervention</div>', unsafe_allow_html=True)
            fig_eff = px.bar(
                effectiveness,
                x="Intervention",
                y="Avg Attendance Change",
                color="Avg Attendance Change",
                color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                labels={"Avg Attendance Change": "Avg Change (pts)"},
            )
            fig_eff.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=350,
                margin=dict(t=20, b=80, l=40, r=20),
                showlegend=False,
            )
            fig_eff.update_xaxes(gridcolor="#1e293b", tickangle=-45)
            fig_eff.update_yaxes(gridcolor="#1e293b")
            st.plotly_chart(fig_eff, width='stretch')

        with col2:
            st.markdown('<div class="section-header">Math Score Change by Intervention</div>', unsafe_allow_html=True)
            fig_math = px.bar(
                effectiveness,
                x="Intervention",
                y="Avg Math Score Change",
                color="Avg Math Score Change",
                color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
                labels={"Avg Math Score Change": "Avg Change (pts)"},
            )
            fig_math.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                height=350,
                margin=dict(t=20, b=80, l=40, r=20),
                showlegend=False,
            )
            fig_math.update_xaxes(gridcolor="#1e293b", tickangle=-45)
            fig_math.update_yaxes(gridcolor="#1e293b")
            st.plotly_chart(fig_math, width='stretch')

        # Gamified Staff Leaderboard
        st.markdown('<div class="section-header">🏆 Top Impact Leaders (Schools)</div>', unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Ranking schools by the most successful interventions logged (where attendance improved).</p>", unsafe_allow_html=True)
        
        # Join interventions to get school names
        interv_with_school = interventions_df.merge(
            students_df[["student_id", "school", "zone"]], on="student_id", how="left"
        ).dropna(subset=["school"])
        
        # Successful = attendance went up
        successful_interventions = interv_with_school[interv_with_school["attendance_after"] > interv_with_school["attendance_before"]]
        leaderboard = successful_interventions.groupby(["school", "zone"]).size().reset_index(name="successful_interventions")
        leaderboard = leaderboard.sort_values("successful_interventions", ascending=False).head(5)
        
        if not leaderboard.empty:
            cols = st.columns(len(leaderboard))
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
            for i, (_, row) in enumerate(leaderboard.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(180deg, rgba(245, 158, 11, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%); 
                                border: 1px solid #334155; border-top: 3px solid #f59e0b; border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="font-size: 2rem;">{medals[i]}</div>
                        <div style="color: #e2e8f0; font-weight: 700; font-size: 1.1rem; margin-top: 8px;">{row['successful_interventions']} Wins</div>
                        <div style="color: #60a5fa; font-size: 0.8rem; margin-top: 4px; line-height: 1.2;">{row['school'].split(' - ')[-1]}</div>
                        <div style="color: #64748b; font-size: 0.7rem; margin-top: 8px;">{row['zone']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No successful interventions logged yet to calculate leaderboard.")

    # Log new intervention
    st.markdown('<div class="section-header">📝 Log New Intervention</div>', unsafe_allow_html=True)

    with st.form("log_intervention"):
        col_a, col_b = st.columns(2)

        with col_a:
            student_options = [
                f"{row['student_id']} — {row['name']}"
                for _, row in students_df.iterrows()
            ]
            log_student = st.selectbox("Student", student_options)
            log_type = st.selectbox("Intervention Type", [
                "Home Visit", "Counselling Session", "Peer Buddy Assignment",
                "Scholarship Application", "Parent-Teacher Meeting",
                "Extra Coaching", "Bicycle Provided", "Uniform Provided",
            ])

        with col_b:
            log_date = st.date_input("Date", value=datetime.today())
            log_notes = st.text_area("Notes", height=80)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            att_before = st.number_input("Attendance Before (%)", 0, 100, 50)
            math_before = st.number_input("Math Score Before", 0, 100, 40)
        with col_m2:
            att_after = st.number_input("Attendance After (%)", 0, 100, 65)
            math_after = st.number_input("Math Score After", 0, 100, 55)

        submitted = st.form_submit_button("💾 Log Intervention", type="primary", width='stretch')

        if submitted:
            log_id = int(log_student.split(" — ")[0])
            new_row = pd.DataFrame([{
                "intervention_id": len(interventions_df) + 1,
                "student_id": log_id,
                "intervention_type": log_type,
                "date": str(log_date),
                "notes": log_notes,
                "attendance_before": att_before,
                "math_before": math_before,
                "attendance_after": att_after,
                "math_after": math_after,
            }])

            base = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base, "data", "interventions.csv")

            updated = pd.concat([interventions_df, new_row], ignore_index=True)
            updated.to_csv(csv_path, index=False)

            att_change = att_after - att_before
            math_change = math_after - math_before

            st.success(
                f"✅ Intervention logged successfully!\n\n"
                f"📊 Attendance change: **{'+' if att_change >= 0 else ''}{att_change}%** | "
                f"Math score change: **{'+' if math_change >= 0 else ''}{math_change}**"
            )

    # Recent interventions
    st.markdown('<div class="section-header">📋 Recent Interventions</div>', unsafe_allow_html=True)

    recent = interventions_df.sort_values("date", ascending=False).head(15).copy()
    # Merge student names
    recent = recent.merge(
        students_df[["student_id", "name"]], on="student_id", how="left"
    )
    recent["att_change"] = recent["attendance_after"] - recent["attendance_before"]
    recent["math_change"] = recent["math_after"] - recent["math_before"]

    display_recent = recent[["date", "name", "intervention_type", "attendance_before",
                              "attendance_after", "att_change", "math_before",
                              "math_after", "math_change"]].copy()
    display_recent.columns = ["Date", "Student", "Intervention", "Att Before", "Att After",
                               "Att Change", "Math Before", "Math After", "Math Change"]

    st.dataframe(display_recent, width='stretch', hide_index=True)


# ===================================================================
# PAGE 8: AI CHATBOT
# ===================================================================
elif page == "🤖 AI Chatbot":
    st.markdown('<div class="main-title">🤖 AI Support Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Ask about zone risk, high-risk schools, priority students, attendance, and action plans</div>', unsafe_allow_html=True)

    student_options = [
        f"{row['student_id']} — {row['name']}"
        for _, row in students_df.iterrows()
    ]
    selected = st.selectbox("Context Student (optional)", ["None"] + student_options, index=0)
    selected_student = None
    if selected != "None":
        selected_id = int(selected.split(" — ")[0])
        selected_student = students_df[students_df["student_id"] == selected_id].iloc[0]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "I can help with:\n- **Which zone has highest risk?**\n- **High risk schools**\n- **Summary / overview**\n- **Top high risk students**\n- **Attendance issues**\n- **What should we do for this student?**"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Type your question...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # For chatbot, pass all_students_df for zone-level queries
        response = generate_chatbot_response(prompt, all_students_df, selected_student=selected_student)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)


# ===================================================================
# PAGE 9: STUDENT DATA ENTRY (Staff only)
# ===================================================================
elif page == "📝 Student Data Entry":
    st.markdown('<div class="main-title">📝 Student Data Entry</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Add new students or update existing student details and attendance</div>', unsafe_allow_html=True)

    tab_update, tab_new = st.tabs(["✏️ Update Existing Student", "➕ Add New Student"])

    with tab_update:
        if students_df.empty:
            st.warning("No students found for the selected school. Try changing your Zone/District/School.")
        else:
            student_options = [
                f"{row['student_id']} — {row['name']} (Class {row['class']}{row['section']})"
                for _, row in students_df.iterrows()
            ]
            selected = st.selectbox("Select Student to Edit", student_options, key="edit_student_select")
            selected_id = int(selected.split(" — ")[0])
            student = students_df[students_df["student_id"] == selected_id].iloc[0]

            with st.form("staff_edit_student"):
                st.markdown(f"**Editing: {student['name']}** — ID: {student['student_id']}")
                e1, e2 = st.columns(2)
                with e1:
                    edited_attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, value=int(student["attendance"]))
                    edited_phone = st.text_input("Phone", value=str(student["phone"]))
                    edited_reason = st.text_input("Dropout Reason", value=str(student["dropout_reason"]))
                    edited_math = st.number_input("Math Score", min_value=0, max_value=100, value=int(student["math_score"]))
                with e2:
                    edited_engagement = st.number_input("Engagement Score", min_value=0, max_value=100, value=int(student["engagement_score"]))
                    edited_address = st.text_area("Address", value=str(student["address"]), height=70)
                    edited_distance = st.number_input("Distance (km)", min_value=0.0, max_value=30.0, value=float(student["distance_km"]), step=0.1)
                    edited_science = st.number_input("Science Score", min_value=0, max_value=100, value=int(student["science_score"]))

                if st.form_submit_button("💾 Save Changes", type="primary", width='stretch'):
                    try:
                        import sqlalchemy
                        engine = get_db_engine()
                        with engine.begin() as conn:
                            # Use text query for safe execution
                            query = sqlalchemy.text("""
                                UPDATE students 
                                SET phone = :phone, address = :address, dropout_reason = :reason, 
                                    attendance = :attendance, engagement_score = :engagement, 
                                    distance_km = :distance, math_score = :math, science_score = :science
                                WHERE student_id = :sid
                            """)
                            conn.execute(query, {
                                "phone": edited_phone.strip(), 
                                "address": edited_address.strip(), 
                                "reason": edited_reason.strip() or "None reported",
                                "attendance": int(edited_attendance),
                                "engagement": int(edited_engagement),
                                "distance": float(edited_distance),
                                "math": int(edited_math),
                                "science": int(edited_science),
                                "sid": selected_id
                            })
                        st.cache_data.clear()
                        st.cache_resource.clear()
                        st.success(f"✅ Student {student['name']} updated safely in the database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating database: {e}")

    with tab_new:
        with st.form("staff_add_student"):
            st.markdown("**Add a new student to your school**")
            n1, n2 = st.columns(2)
            with n1:
                new_name = st.text_input("Student Name")
                new_gender = st.selectbox("Gender", ["Male", "Female"])
                new_class = st.selectbox("Class", [6, 7, 8, 9, 10])
                new_section = st.selectbox("Section", ["A", "B", "C"])
                new_phone = st.text_input("Phone Number")
                new_school = st.text_input("School Name", value=str(st.session_state.staff_district) + " Gov. High School")
                new_attendance = st.number_input("Attendance (%)", min_value=0, max_value=100, value=45)
                new_math = st.number_input("Math Score", min_value=0, max_value=100, value=30)
                new_location = st.selectbox("Location Type", ["City", "Village"])
            with n2:
                new_address = st.text_area("Address", height=70)
                new_income = st.selectbox("Family Income", ["low", "medium", "high"])
                new_parent_edu = st.selectbox("Parent Education", ["none", "primary", "secondary", "graduate"])
                new_distance = st.number_input("Distance (km)", min_value=0.0, max_value=30.0, value=9.0, step=0.1)
                new_sibling = st.selectbox("Sibling Dropout", ["no", "yes"], index=1)
                new_science = st.number_input("Science Score", min_value=0, max_value=100, value=30)
                new_language = st.number_input("Language Score", min_value=0, max_value=100, value=30)
                new_engagement = st.number_input("Engagement Score", min_value=0, max_value=100, value=40)

            if st.form_submit_button("➕ Add Student", type="primary", width='stretch'):
                if not new_name.strip():
                    st.error("Student name is required.")
                else:
                    try:
                        import sqlalchemy
                        engine = get_db_engine()
                        with engine.begin() as conn:
                            # Get new ID
                            res = conn.execute(sqlalchemy.text("SELECT MAX(student_id) FROM students"))
                            max_id = res.scalar() or 0
                            new_id = max_id + 1
                            
                            query = sqlalchemy.text("""
                                INSERT INTO students (
                                    student_id, name, gender, class, section, school, zone, district, state, phone, address, 
                                    attendance, math_score, science_score, language_score, meal_participation, distance_km, 
                                    sibling_dropout, family_income, parent_education, engagement_score, dropout_reason, dropout_risk, location_type
                                ) VALUES (
                                    :sid, :name, :gender, :cls, :sec, :school, :zone, :district, 'Tamil Nadu', :phone, :address,
                                    :att, :math, :sci, :lang, 'yes', :dist, :sib, :inc, :pedu, :eng, 'None reported', 0, :loc
                                )
                            """)
                            conn.execute(query, {
                                "sid": new_id, "name": new_name.strip(), "gender": new_gender, "cls": int(new_class), "sec": new_section,
                                "school": new_school.strip(), "zone": st.session_state.staff_zone, "district": st.session_state.staff_district, 
                                "phone": new_phone.strip(), "address": new_address.strip(), "att": int(new_attendance), 
                                "math": int(new_math), "sci": int(new_science), "lang": int(new_language), "dist": float(new_distance),
                                "sib": new_sibling, "inc": new_income, "pedu": new_parent_edu, "eng": int(new_engagement), "loc": new_location
                            })
                        st.cache_data.clear()
                        st.cache_resource.clear()
                        st.success(f"✅ Added new student {new_name} to {new_school} in the database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding student to database: {e}")
                    new_id = int(source_df["student_id"].max()) + 1
                    new_row = {
                        "student_id": new_id,
                        "name": new_name.strip(),
                        "gender": new_gender,
                        "class": new_class,
                        "section": new_section,
                        "school": selected_school if selected_school else "Unknown",
                        "zone": st.session_state.get("staff_zone", "North Zone"),
                        "district": st.session_state.get("staff_district", "Chennai"),
                        "location_type": new_location,
                        "state": "Tamil Nadu",
                        "phone": new_phone.strip() or "+91-00000-00000",
                        "address": new_address.strip() or "Address not available",
                        "attendance": int(new_attendance),
                        "math_score": int(new_math),
                        "science_score": int(new_science),
                        "language_score": int(new_language),
                        "meal_participation": "yes",
                        "distance_km": float(new_distance),
                        "sibling_dropout": new_sibling,
                        "family_income": new_income,
                        "parent_education": new_parent_edu,
                        "engagement_score": int(new_engagement),
                        "dropout_reason": "None reported",
                        "dropout_risk": 0,
                    }
                    source_df = pd.concat([source_df, pd.DataFrame([new_row])], ignore_index=True)
                    source_df.to_csv(csv_path, index=False)
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.success(f"✅ Student **{new_name}** added with ID {new_id}!")
                    st.rerun()
