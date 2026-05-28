"""
CoughGPT Streamlit Frontend
============================
UI-only layer. Calls FastAPI backend via HTTP for all ML/AI operations.

Run: streamlit run frontend/app.py
"""

import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------

BACKEND_URL = os.getenv("COUGHGPT_BACKEND_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_SECRET_KEY", "coughgpt-dev-secret-change-in-production")

st.set_page_config(
    page_title="CoughGPT - AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# API CLIENT
# -----------------------------


def api_call(endpoint: str, payload: dict) -> dict | None:
    """Make authenticated POST request to backend API."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}{endpoint}",
            json=payload,
            headers={"X-API-Key": API_KEY},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Make sure the FastAPI server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ API Error: {e.response.status_code}")
        return None
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. Please try again.")
        return None


def check_backend_health() -> bool:
    """Check if backend is alive."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        data = resp.json()
        return data.get("status") == "ok" and data.get("models_loaded", False)
    except Exception:
        return False


# -----------------------------
# NEOBRUTALISM STYLING
# -----------------------------

st.markdown("""
    <style>
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Space+Mono:wght@400;700&display=swap');
        
        * {
            font-family: 'Space Grotesk', sans-serif;
        }
        
        .stApp {
            background-color: #F5F5F5;
        }
        
        /* Force dark text in main content area */
        .stApp [data-testid="stMainBlockContainer"] * {
            color: #000 !important;
        }
        
        /* Override for dark-bg elements (white text on black) — higher specificity */
        .stApp [data-testid="stMainBlockContainer"] .footer-neo,
        .stApp [data-testid="stMainBlockContainer"] .footer-neo *,
        .stApp [data-testid="stMainBlockContainer"] .neo-card-dark,
        .stApp [data-testid="stMainBlockContainer"] .neo-card-dark *,
        .stApp [data-testid="stMainBlockContainer"] .hero-badge-dark,
        .stApp [data-testid="stMainBlockContainer"] .hero-badge-dark * {
            color: #FFF !important;
        }
        
        /* Button text */
        .stApp [data-testid="stMainBlockContainer"] .stButton button,
        .stApp [data-testid="stMainBlockContainer"] .stButton button * {
            color: #FFF !important;
        }
        .stApp [data-testid="stMainBlockContainer"] .stButton button:hover,
        .stApp [data-testid="stMainBlockContainer"] .stButton button:hover * {
            color: #000 !important;
        }
        
        /* Text area label */
        .stTextArea label, .stTextArea label * {
            color: #000 !important;
            font-weight: 700 !important;
        }
        
        /* Tooltip Info Icon */
        [data-testid="stTooltipIcon"],
        [data-testid="stTooltipIcon"] * {
            color: #000 !important;
            fill: #000 !important;
        }
        
        /* Neobrutalism Header */
        .neo-hero {
            background: #FFE500;
            border: 5px solid #000;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
            box-shadow: 12px 12px 0px #000;
            position: relative;
        }
        
        .neo-title {
            font-size: 4rem;
            font-weight: 700;
            color: #000;
            margin: 0;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: -2px;
        }
        
        .neo-subtitle {
            font-size: 1.2rem;
            color: #000;
            text-align: center;
            margin-top: 1rem;
            font-weight: 600;
            font-family: 'Space Mono', monospace;
        }
        
        .neo-emoji {
            font-size: 5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* Neobrutalism Cards */
        .neo-card {
            background: #FFF;
            border: 4px solid #000;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 8px 8px 0px #000;
            transition: all 0.2s ease;
        }
        
        .neo-card:hover {
            transform: translate(4px, 4px);
            box-shadow: 4px 4px 0px #000;
        }
        
        /* Feature Boxes */
        .feature-neo {
            background: #FFF;
            border: 4px solid #000;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 6px 6px 0px #000;
            transition: all 0.2s ease;
        }
        
        .feature-neo:hover {
            transform: translate(-2px, -2px);
            box-shadow: 8px 8px 0px #000;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #000;
            margin: 0.5rem 0;
            text-transform: uppercase;
        }
        
        .feature-desc {
            font-size: 0.95rem;
            color: #333;
            font-weight: 600;
        }
        
        /* Sidebar Styles */
        [data-testid="stSidebar"] {
            background: #000;
            border-right: 5px solid #000;
        }
        
        [data-testid="stSidebar"] * {
            color: #FFF !important;
        }
        
        /* Hide default radio */
        [data-testid="stSidebar"] .stRadio {
            display: none;
        }
        
        /* Navigation Menu */
        .nav-menu {
            margin: 2rem 0;
        }
        
        .nav-item {
            background: #FFF;
            color: #000 !important;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border: 3px solid #FFF;
            font-weight: 700;
            font-size: 1.1rem;
            text-transform: uppercase;
            cursor: pointer;
            box-shadow: 5px 5px 0px #FFE500;
            transition: all 0.2s ease;
            text-align: center;
            text-decoration: none;
            display: block;
        }
        
        .nav-item:hover {
            transform: translate(2px, 2px);
            box-shadow: 3px 3px 0px #FFE500;
            background: #FFE500;
        }
        
        .nav-item.active {
            background: #FFE500;
            box-shadow: 5px 5px 0px #FFF;
        }
        
        /* Sidebar Stats */
        .stat-box {
            background: #FFE500;
            border: 3px solid #FFF;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 5px 5px 0px #FFF;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #000;
            font-family: 'Space Mono', monospace;
        }
        
        .stat-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #000;
            text-transform: uppercase;
            margin-top: 0.5rem;
        }
        
        /* Button Styles */
        .stButton button {
            background: #000;
            color: #FFF;
            font-weight: 700;
            border: 4px solid #000;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 6px 6px 0px #000;
            transition: all 0.2s ease;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        .stButton button:hover {
            transform: translate(3px, 3px);
            box-shadow: 3px 3px 0px #000;
            background: #FFE500;
            color: #000;
        }
        
        /* Input Styles */
        .stTextArea textarea, .stTextInput input {
            border: 4px solid #000 !important;
            padding: 1rem;
            font-size: 1rem;
            background: #FFF;
            color: #000 !important;
            caret-color: #000 !important;
            font-family: 'Space Mono', monospace;
            box-shadow: 4px 4px 0px #000;
        }
        
        .stTextArea textarea:focus, .stTextInput input:focus {
            border: 4px solid #000 !important;
            box-shadow: 6px 6px 0px #000;
        }
        
        /* Drug Items */
        .drug-neo {
            background: #FFF;
            border: 3px solid #000;
            padding: 1rem 1.5rem;
            margin: 0.8rem 0;
            box-shadow: 4px 4px 0px #000;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 2rem;
            font-weight: 700;
            color: #000;
            text-transform: uppercase;
            margin: 2rem 0 1rem 0;
            padding: 0.5rem 1rem;
            background: #FFE500;
            border: 4px solid #000;
            box-shadow: 6px 6px 0px #000;
            display: inline-block;
        }
        
        /* Alert Boxes */
        .stAlert {
            border: 4px solid #000 !important;
            box-shadow: 4px 4px 0px #000 !important;
            font-weight: 600;
        }
        
        /* Info Box */
        .info-neo {
            background: #FFF;
            border: 4px solid #000;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 6px 6px 0px #000;
            font-weight: 600;
            color: #000;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        
        /* Success Box */
        .success-neo {
            background: #FFF;
            border: 4px solid #000;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 6px 6px 0px #000;
            font-weight: 700;
            color: #000;
            font-size: 1.3rem;
        }
        
        /* Warning Box */
        .warning-neo {
            background: #FFF;
            border: 4px solid #000;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 6px 6px 0px #000;
            font-weight: 700;
            color: #000;
        }
        
        /* Footer */
        .footer-neo {
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            background: #000;
            color: #FFF;
            border: 4px solid #000;
            box-shadow: 8px 8px 0px #000;
            font-weight: 700;
            font-family: 'Space Mono', monospace;
        }
        
        /* Disclaimer Badge */
        .disclaimer-badge {
            background: #FFF;
            color: #000 !important;
            padding: 1.5rem;
            border: 3px solid #FFE500;
            margin: 2rem 0;
            font-weight: 600;
            box-shadow: 5px 5px 0px #FFE500;
            line-height: 1.6;
        }
        
        .disclaimer-badge b {
            color: #000 !important;
        }
        
        /* Critical Disclaimer Banner */
        .disclaimer-critical {
            background: #FFF5F5;
            color: #000 !important;
            padding: 2rem;
            border: 4px solid #FF4444;
            margin: 2rem 0;
            font-weight: 600;
            box-shadow: 8px 8px 0px #FF4444;
            line-height: 1.8;
        }
        
        .disclaimer-critical b {
            color: #CC0000 !important;
        }
        
        .disclaimer-critical ul {
            margin: 1rem 0;
            padding-left: 1.5rem;
        }
        
        .disclaimer-critical li {
            margin: 0.5rem 0;
        }
        
        /* List Styles */
        ul, ol {
            font-weight: 600;
            line-height: 1.8;
        }
        
        h3 {
            font-weight: 700;
            color: #000;
            text-transform: uppercase;
            margin-top: 1.5rem;
        }
        
        /* Sidebar Logo */
        .sidebar-logo {
            text-align: center;
            padding: 2rem 1rem;
            background: #FFE500;
            border: 4px solid #FFF;
            margin: 1rem 0;
            box-shadow: 5px 5px 0px #FFF;
        }
        
        .sidebar-logo-icon {
            font-size: 4rem;
            margin-bottom: 0.5rem;
        }
        
        .sidebar-logo-text {
            font-size: 1.8rem;
            font-weight: 700;
            color: #000;
            margin: 0;
            text-transform: uppercase;
        }
        
        .sidebar-logo-tagline {
            font-size: 0.85rem;
            color: #000;
            font-weight: 600;
            margin-top: 0.3rem;
            font-family: 'Space Mono', monospace;
        }

        /* Backend Status */
        .status-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border: 2px solid #000;
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            font-family: 'Space Mono', monospace;
            margin-top: 0.5rem;
        }
        .status-online { background: #00FF88; color: #000; }
        .status-offline { background: #FF4444; color: #FFF; }
    </style>
""", unsafe_allow_html=True)


# -----------------------------
# SESSION STATE
# -----------------------------

if "page" not in st.session_state:
    st.session_state.page = "HOME"

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:
    # Logo Section
    st.markdown("""
        <div class='sidebar-logo'>
            <div class='sidebar-logo-icon'>🩺</div>
            <div class='sidebar-logo-text'>COUGHGPT</div>
            <div class='sidebar-logo-tagline'>AI Health Assistant</div>
        </div>
    """, unsafe_allow_html=True)

    # Backend Status
    backend_online = check_backend_health()
    status_class = "status-online" if backend_online else "status-offline"
    status_text = "● ONLINE" if backend_online else "● OFFLINE"
    st.markdown(
        f"<div style='text-align:center'><span class='status-badge {status_class}'>{status_text}</span></div>",
        unsafe_allow_html=True,
    )

    # Navigation Menu
    st.markdown("<div class='nav-menu'>", unsafe_allow_html=True)

    if st.button("🏠 HOME", use_container_width=True, key="nav_home"):
        st.session_state.page = "HOME"

    if st.button("ℹ️ ABOUT", use_container_width=True, key="nav_about"):
        st.session_state.page = "ABOUT"

    if st.button("📞 CONTACT", use_container_width=True, key="nav_contact"):
        st.session_state.page = "CONTACT"

    st.markdown("</div>", unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
        <div class='disclaimer-badge'>
            <b>⚠️ MEDICAL DISCLAIMER</b><br><br>
            This is a <b>student learning project</b> — NOT a medical tool. Predictions are NOT clinically validated. Do NOT self-medicate. Always consult a qualified doctor.
        </div>
    """, unsafe_allow_html=True)


# -----------------------------
# HOME PAGE
# -----------------------------

if st.session_state.page == "HOME":

    # Compact Hero Section with Features
    st.markdown("""
        <div class='neo-hero'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-bottom: 1rem;'>
                <span style='font-size: 3.5rem;'>🩺</span>
                <h1 class='neo-title' style='font-size: 3rem; margin: 0; text-transform: none;'>CoughGPT</h1>
            </div>
            <p class='neo-subtitle' style='margin-bottom: 1.5rem;'>// AI-POWERED HEALTH ANALYSIS SYSTEM //</p>
            <div style='display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;'>
                <div class='hero-badge-dark' style='background: #000; padding: 0.6rem 1.2rem; border: 3px solid #000; box-shadow: 3px 3px 0px #000; font-weight: 700; font-size: 0.9rem;'>
                    🔬 ANALYZE
                </div>
                <div class='hero-badge-dark' style='background: #000; padding: 0.6rem 1.2rem; border: 3px solid #000; box-shadow: 3px 3px 0px #000; font-weight: 700; font-size: 0.9rem;'>
                    💊 RECOMMEND
                </div>
                <div class='hero-badge-dark' style='background: #000; padding: 0.6rem 1.2rem; border: 3px solid #000; box-shadow: 3px 3px 0px #000; font-weight: 700; font-size: 0.9rem;'>
                    🤖 EXPLAIN
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Input Section
    st.markdown("<div class='section-header'>📝 INPUT</div>", unsafe_allow_html=True)

    user_input = st.text_area(
        "ENTER SYMPTOMS OR CONDITION:",
        placeholder="SYMPTOMS: fever, cough, chest pain\nCONDITION: Type 2 Diabetes",
        height=120,
        help="Separate symptoms with commas",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 ANALYZE NOW", use_container_width=True)

    if analyze_button and user_input:
        if not backend_online:
            st.error("⚠️ Backend server is offline. Start it with: `uvicorn backend.main:app --host 127.0.0.1 --port 8000`")
        else:
            with st.spinner("🧠 Analyzing with AI..."):
                result = api_call("/api/analyze", {"user_input": user_input})

            if result:
                # Language detection info
                st.info(f"🌐 **Detected Language:** {result['detected_language']}")

                if result["language_code"] != "en":
                    st.success(f"📝 **Translation:** {result['english_input']}")

                st.markdown("<br>", unsafe_allow_html=True)

                if result["input_type"] == "symptoms":
                    # Disease Result
                    st.markdown("<div class='section-header'>🧬 DIAGNOSIS</div>", unsafe_allow_html=True)
                    disease_display = result.get("disease_translated") or result.get("disease", "Unknown")
                    st.markdown(f"""
                        <div class='success-neo'>
                            {disease_display}
                        </div>
                    """, unsafe_allow_html=True)

                    if result["language_code"] != "en" and result.get("disease"):
                        st.caption(f"English: {result['disease']}")

                # Drug Recommendations
                st.markdown("<div class='section-header'>💊 MEDICATIONS</div>", unsafe_allow_html=True)

                if result["input_type"] == "condition":
                    condition_display = result["english_input"]
                    st.markdown(
                        f"<p style='font-weight: 700; font-size: 1.1rem;'>FOR: {condition_display.upper()}</p>",
                        unsafe_allow_html=True,
                    )

                if result["drugs"]:
                    for idx, drug in enumerate(result["drugs"]):
                        st.markdown(f"""
                            <div class='drug-neo'>
                                [{idx + 1}] {drug}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class='warning-neo'>
                            ⚠️ NO SPECIFIC RECOMMENDATIONS AVAILABLE
                        </div>
                    """, unsafe_allow_html=True)

                # AI Explanation
                st.markdown("<div class='section-header'>🧑‍⚕️ EXPLANATION</div>", unsafe_allow_html=True)
                explanation = result.get("explanation_translated") or result.get("explanation", "")
                st.markdown(f"""
                    <div class='info-neo'>
                        {explanation}
                    </div>
                """, unsafe_allow_html=True)

                # Medical Disclaimer Banner
                st.markdown("""
                    <div class='disclaimer-critical'>
                        <b>⚠️ IMPORTANT MEDICAL DISCLAIMER</b><br><br>
                        CoughGPT is a <b>student/learning project</b> built purely for <b>educational and demonstration purposes</b>.
                        <ul>
                            <li>The disease predictions and drug recommendations are <b>NOT medically verified</b> and <b>NOT clinically validated</b>.</li>
                            <li><b>Do NOT take any medication</b> based on what this app suggests.</li>
                            <li><b>Always consult a qualified medical professional</b> for health concerns, diagnosis, and treatment.</li>
                            <li>If you are experiencing a medical emergency, <b>call your local emergency services immediately</b>.</li>
                        </ul>
                        <b>Use this project only to explore how ML pipelines and LLM integrations work — not as a health tool.</b>
                    </div>
                """, unsafe_allow_html=True)

    elif analyze_button:
        st.markdown("""
            <div class='warning-neo'>
                ⚠️ PLEASE ENTER SYMPTOMS OR CONDITION
            </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class='footer-neo'>
            MADE WITH STREAMLIT × FASTAPI × FASTTEXT × GOOGLE GEMINI<br>
            
        </div>
    """, unsafe_allow_html=True)


# -----------------------------
# ABOUT PAGE
# -----------------------------

elif st.session_state.page == "ABOUT":
    st.markdown("""
        <div class='neo-hero'>
            <div class='neo-emoji'>ℹ️</div>
            <h1 class='neo-title'>ABOUT</h1>
            <p class='neo-subtitle'>// DEMOCRATIZING HEALTHCARE WITH AI //</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='neo-card'>
            <h3>🎯 MISSION</h3>
            <p>CoughGPT makes preliminary health insights accessible through AI. We combine machine learning with natural language processing to help you understand symptoms better.</p>
        </div>
        
        <div class='neo-card'>
            <h3>🔧 HOW IT WORKS</h3>
            <ol>
                <li><b>SYMPTOM INPUT:</b> Natural language description</li>
                <li><b>ML ANALYSIS:</b> FastText embeddings + trained classifiers</li>
                <li><b>DRUG MATCHING:</b> Evidence-based recommendations</li>
                <li><b>AI EXPLANATION:</b> Google Gemini provides insights</li>
            </ol>
        </div>
        
        <div class='neo-card'>
            <h3>🧬 TECH STACK</h3>
            <ul>
                <li><b>FRONTEND:</b> Streamlit</li>
                <li><b>BACKEND:</b> FastAPI</li>
                <li><b>ML MODELS:</b> Scikit-learn, FastText</li>
                <li><b>AI ENGINE:</b> Google Gemini 2.5 Flash</li>
                <li><b>DATASET:</b> UCI ML Drug Review</li>
            </ul>
        </div>
        
        <div class='disclaimer-critical'>
            <b>⚠️ IMPORTANT MEDICAL DISCLAIMER</b><br><br>
            CoughGPT is a <b>student/learning project</b> built purely for <b>educational and demonstration purposes</b>.
            <ul>
                <li>The disease predictions and drug recommendations are <b>NOT medically verified</b> and <b>NOT clinically validated</b>.</li>
                <li><b>Do NOT take any medication</b> based on what this app suggests.</li>
                <li><b>Always consult a qualified medical professional</b> for health concerns, diagnosis, and treatment.</li>
                <li>The creators are <b>not medical professionals</b> and accept <b>no responsibility or liability</b> for any actions taken based on app outputs.</li>
                <li>If you are experiencing a medical emergency, <b>call your local emergency services immediately</b>.</li>
            </ul>
            <b>Use this project only to explore how ML pipelines and LLM integrations work — not as a health tool.</b>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------
# CONTACT PAGE
# -----------------------------

elif st.session_state.page == "CONTACT":
    st.markdown("""
        <div class='neo-hero'>
            <div class='neo-emoji'>📞</div>
            <h1 class='neo-title'>CONTACT</h1>
            <p class='neo-subtitle'>// GET IN TOUCH //</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class='neo-card'>
                <h3>👨‍💻 DEVELOPER</h3>
                <p><b>PARV SHRIVASTAVA</b></p>
                <p>ML Enthusiast</p>
            </div>
            
            <div class='neo-card'>
                <h3>📧 EMAIL</h3>
                <p style='font-family: Space Mono, monospace;'><b>parv2410shri@gmail.com</b></p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class='neo-card'>
                <h3>🐙 GITHUB</h3>
                <p style='font-family: Space Mono, monospace;'><b>github.com/parvv-24</b></p>
                <p>Check out more projects</p>
            </div>
            
            <div class='neo-card'>
                <h3>💡 FEEDBACK</h3>
                <p>Your feedback helps us improve! Reach out with suggestions or bug reports.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div class='neo-card neo-card-dark' style='background: #000; text-align: center;'>
            <h3 style='color: #FFF;'>🤝 OPEN TO COLLABORATION</h3>
            <p style='color: #FFF;'>Interested in healthcare AI or ML applications? Let's connect!</p>
        </div>
    """, unsafe_allow_html=True)
