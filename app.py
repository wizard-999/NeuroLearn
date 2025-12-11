"""
NeuroLearn: Accessible Learning Hub for Neurodivergent Students
Complete UI redesign with role-based accessibility modes and light/dark themes
"""

from datetime import date, timedelta
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

from modules import (
    database,
    gamification,
    pdf_utils,
    quiz_generator,
    simplify_text,
    tts_module,
)

# ============================================================================
# BACKEND CONFIGURATION - API Keys
# ============================================================================

# Gemini API key - hardcoded in backend
GEMINI_API_KEY = ""

# ============================================================================
# CSS THEME SYSTEM - Role-Based + Light/Dark Mode
# ============================================================================

def get_css(role: str, theme: str) -> str:
    """
    Generate CSS based on role (Dyslexic, ADHD, Combined) and theme (Light, Dark).
    Returns complete CSS string with all styling rules.
    """
    
    # Color palettes based on theme
    if theme == "Dark":
        # Dark mode colors
        bg_primary = "#0E0F11"
        bg_secondary = "#1A1C1F"
        bg_card = "#1F2225"
        text_primary = "#E9E9E9"
        text_secondary = "#B8B8B8"
        border_color = "#2D3135"
        accent_blue = "#4A9EFF"
        accent_teal = "#5BC0BE"
        accent_lavender = "#9B7EDE"
        success_bg = "#1E3A1E"
        success_text = "#6BCF7F"
        error_bg = "#3A1E1E"
        error_text = "#FF6B6B"
        info_bg = "#1E2A3A"
        info_text = "#6BA3FF"
    else:
        # Light mode colors
        bg_primary = "#FFFFFF"
        bg_secondary = "#F8F9FA"
        bg_card = "#F3F4F6"
        text_primary = "#1F1F1F"
        text_secondary = "#4A4A4A"
        border_color = "#E5E7EB"
        accent_blue = "#3B82F6"
        accent_teal = "#14B8A6"
        accent_lavender = "#A78BFA"
        success_bg = "#D1FAE5"
        success_text = "#065F46"
        error_bg = "#FEE2E2"
        error_text = "#991B1B"
        info_bg = "#DBEAFE"
        info_text = "#1E40AF"
    
    # Font settings based on role
    if role == "Dyslexic":
        font_family = "'Atkinson Hyperlegible', 'Comic Sans MS', sans-serif"
        base_font_size = "19px"
        h1_size = "34px"
        h2_size = "28px"
        h3_size = "24px"
        letter_spacing = "0.6px"
        line_height = "1.75"
        max_width = "900px"
        card_padding = "32px"
        section_spacing = "2rem"
    elif role == "ADHD":
        font_family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
        base_font_size = "18px"
        h1_size = "36px"
        h2_size = "30px"
        h3_size = "24px"
        letter_spacing = "0px"
        line_height = "1.7"
        max_width = "1000px"
        card_padding = "36px"
        section_spacing = "2.5rem"
    else:  # Combined
        font_family = "'Atkinson Hyperlegible', 'Comic Sans MS', sans-serif"
        base_font_size = "21px"
        h1_size = "38px"
        h2_size = "32px"
        h3_size = "26px"
        letter_spacing = "0.7px"
        line_height = "1.85"
        max_width = "850px"
        card_padding = "40px"
        section_spacing = "3rem"
    
    # Background gradient based on role and theme
    if role == "ADHD":
        if theme == "Dark":
            bg_gradient = "linear-gradient(135deg, #0E1419 0%, #0F1A1F 100%)"
        else:
            bg_gradient = "linear-gradient(135deg, #E8F4F8 0%, #F0F8F8 100%)"
    elif role == "Dyslexic":
        if theme == "Dark":
            bg_gradient = f"linear-gradient(135deg, {bg_primary} 0%, #151719 100%)"
        else:
            bg_gradient = "#FAFBFC"
    else:  # Combined
        if theme == "Dark":
            bg_gradient = f"linear-gradient(135deg, {bg_primary} 0%, #121416 100%)"
        else:
            bg_gradient = "linear-gradient(135deg, #F5F7FA 0%, #EEF2F5 100%)"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Inter:wght@400;500;600;700&display=swap');
    
    /* ===== GLOBAL RESET ===== */
    * {{
        font-family: {font_family} !important;
        letter-spacing: {letter_spacing} !important;
    }}
    
    /* ===== MAIN APP BACKGROUND ===== */
    .stApp {{
        background: {bg_gradient} !important;
    }}
    
    /* ===== MAIN CONTAINER ===== */
    .main .block-container {{
        max-width: {max_width} !important;
        padding: 3rem 2.5rem !important;
    }}
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown, .stText {{
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        color: {text_primary} !important;
        font-style: normal !important;
    }}
    
    h1 {{
        font-size: {h1_size} !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        line-height: 1.4 !important;
    }}
    
    h2 {{
        font-size: {h2_size} !important;
        font-weight: 600 !important;
        margin-top: {section_spacing} !important;
        margin-bottom: 1.5rem !important;
        line-height: 1.5 !important;
    }}
    
    h3 {{
        font-size: {h3_size} !important;
        font-weight: 600 !important;
        margin-bottom: 1.25rem !important;
    }}
    
    /* ===== CARDS ===== */
    .card-container {{
        background-color: {bg_card} !important;
        border-radius: 16px !important;
        padding: {card_padding} !important;
        margin: {section_spacing} 0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border: 2px solid {border_color} !important;
    }}
    
    /* ===== BUTTONS ===== */
    .stButton > button {{
        font-size: {base_font_size} !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        border: 2px solid {accent_blue} !important;
        background-color: {accent_blue} !important;
        color: white !important;
        font-weight: 600 !important;
        min-height: 52px !important;
        letter-spacing: {letter_spacing} !important;
        transition: none !important;
        width: 100% !important;
    }}
    
    .stButton > button:hover {{
        background-color: {accent_blue} !important;
        opacity: 0.9 !important;
        border-color: {accent_blue} !important;
    }}
    
    .stButton > button:focus {{
        outline: 4px solid {accent_blue} !important;
        outline-offset: 3px !important;
    }}
    
    .stButton > button:disabled {{
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }}
    
    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        font-size: {base_font_size} !important;
        padding: 14px 16px !important;
        border-radius: 10px !important;
        border: 2px solid {border_color} !important;
        background-color: {bg_primary} !important;
        color: {text_primary} !important;
        line-height: {line_height} !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {accent_blue} !important;
        outline: 3px solid {accent_blue} !important;
        outline-offset: 2px !important;
    }}
    
    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {{
        gap: 1.25rem !important;
        margin: 1.5rem 0 !important;
    }}
    
    .stRadio > div > label {{
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        padding: 10px 0 !important;
        color: {text_primary} !important;
    }}
    
    /* ===== SELECTBOX ===== */
    .stSelectbox > div > div > select {{
        font-size: {base_font_size} !important;
        padding: 14px 16px !important;
        border-radius: 10px !important;
        min-height: 52px !important;
        background-color: {bg_primary} !important;
        color: {text_primary} !important;
        border: 2px solid {border_color} !important;
    }}
    
    /* ===== SLIDER ===== */
    .stSlider > div > div {{
        padding: 1rem 0 !important;
    }}
    
    /* ===== SIDEBAR ===== */
    .css-1d391kg {{
        background: {bg_secondary} !important;
    }}
    
    .stSidebar {{
        background: {bg_secondary} !important;
    }}
    
    .stSidebar .stMarkdown {{
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        color: {text_primary} !important;
    }}
    
    .stSidebar .stRadio > div > label {{
        font-size: {base_font_size} !important;
    }}
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader > div {{
        padding: 24px !important;
        border-radius: 12px !important;
        border: 2px dashed {border_color} !important;
        background-color: {bg_card} !important;
        margin: 1rem 0 !important;
    }}
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem !important;
        margin-bottom: 2rem !important;
        border-bottom: 2px solid {border_color} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-size: {base_font_size} !important;
        padding: 14px 28px !important;
        color: {text_secondary} !important;
        font-weight: 500 !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {accent_blue} !important;
        border-bottom: 3px solid {accent_blue} !important;
    }}
    
    /* ===== SUCCESS/ERROR/INFO MESSAGES ===== */
    .stSuccess {{
        background-color: {success_bg} !important;
        color: {success_text} !important;
        padding: 18px 24px !important;
        border-radius: 12px !important;
        border-left: 4px solid {success_text} !important;
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        margin: 1.5rem 0 !important;
    }}
    
    .stError {{
        background-color: {error_bg} !important;
        color: {error_text} !important;
        padding: 18px 24px !important;
        border-radius: 12px !important;
        border-left: 4px solid {error_text} !important;
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        margin: 1.5rem 0 !important;
    }}
    
    .stInfo {{
        background-color: {info_bg} !important;
        color: {info_text} !important;
        padding: 18px 24px !important;
        border-radius: 12px !important;
        border-left: 4px solid {info_text} !important;
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        margin: 1.5rem 0 !important;
    }}
    
    .stWarning {{
        background-color: {info_bg} !important;
        color: {info_text} !important;
        padding: 18px 24px !important;
        border-radius: 12px !important;
        border-left: 4px solid {info_text} !important;
        font-size: {base_font_size} !important;
        line-height: {line_height} !important;
        margin: 1.5rem 0 !important;
    }}
    
    /* ===== CAPTION ===== */
    .stCaption {{
        color: {text_secondary} !important;
        font-size: calc({base_font_size} - 2px) !important;
    }}
    
    /* ===== SPACING ===== */
    .element-container {{
        margin-bottom: {section_spacing} !important;
    }}
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {{
        font-size: calc({base_font_size} * 1.5) !important;
        font-weight: 700 !important;
        color: {accent_blue} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: {base_font_size} !important;
        color: {text_secondary} !important;
    }}
    
    /* ===== CHECKBOX ===== */
    .stCheckbox > label {{
        font-size: {base_font_size} !important;
        color: {text_primary} !important;
        line-height: {line_height} !important;
    }}
    
    /* ===== TEXT AREA SPECIFIC ===== */
    .stTextArea > div > div > textarea {{
        min-height: 400px !important;
    }}
    
    /* ===== REMOVE CLUTTER ===== */
    .stMarkdown img {{
        display: none !important;
    }}
    
    /* ===== QUIZ RADIO STYLING ===== */
    .quiz-question {{
        background-color: {bg_card} !important;
        padding: 24px !important;
        border-radius: 12px !important;
        margin: 1.5rem 0 !important;
        border: 2px solid {border_color} !important;
    }}
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    </style>
    """


def inject_css(role: str, theme: str) -> None:
    """Inject the appropriate CSS based on user role and theme."""
    css = get_css(role, theme)
    st.markdown(css, unsafe_allow_html=True)


# ============================================================================
# PAGE INITIALIZATION
# ============================================================================

def init_page() -> None:
    """Initialize the page configuration."""
    st.set_page_config(
        page_title="NeuroLearn",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ============================================================================
# SIDEBAR LAYOUT
# ============================================================================

def sidebar_layout() -> Dict[str, Any]:
    """Create the sidebar with role selection, theme toggle, and settings."""
    
    # User Profile Section
    st.sidebar.markdown("### 🎯 User Profile")
    
    role = st.sidebar.radio(
        "**Learning Mode:**",
        ["Dyslexic", "ADHD", "Combined"],
        index=0,
        help="Select the interface mode that works best for you. The UI will adapt automatically.",
    )
    
    st.sidebar.markdown("---")
    
    # Theme Toggle
    st.sidebar.markdown("### 🌗 Theme")
    theme = st.sidebar.radio(
        "**Color Theme:**",
        ["Light", "Dark"],
        index=0,
        help="Choose between light and dark mode.",
    )
    
    st.sidebar.markdown("---")
    
    # Document Upload
    st.sidebar.markdown("### 📄 Document Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload a PDF document to begin learning.",
        label_visibility="collapsed",
    )
    
    st.sidebar.markdown("---")
    
    # Reading Settings
    st.sidebar.markdown("### ⚙️ Reading Settings")
    highlight_speed = st.sidebar.slider(
        "Reading Speed (wpm)",
        min_value=80,
        max_value=220,
        value=140,
        help="Adjust the speed for text-to-speech reading.",
    )
    
    st.sidebar.checkbox(
        "Enable adaptive suggestions",
        value=True,
        help="Get personalized learning suggestions.",
    )
    
    st.sidebar.markdown("---")
    
    # Optional OpenAI API Key (for quiz generation - optional, Gemini is used as fallback)
    st.sidebar.markdown("### 🔑 API Configuration (Optional)")
    
    st.sidebar.markdown("**OpenAI API Key** (Optional)")
    openai_key = st.sidebar.text_input(
        "OpenAI Key",
        type="password",
        label_visibility="collapsed",
        help="Optional: Enter your OpenAI API key for quiz generation. Gemini will be used if not provided.",
    )
    
    return {
        "role": role,
        "theme": theme,
        "uploaded_file": uploaded_file,
        "highlight_speed": highlight_speed,
        "openai_key": openai_key,
    }


# ============================================================================
# READER TAB
# ============================================================================

def _render_reader_tab(state: Dict[str, Any]) -> None:
    """Render the assistive reader tab with improved UI."""
    st.markdown("## 📖 Assistive Reader")
    
    uploaded_file = state.get("uploaded_file")
    highlight_speed = state.get("highlight_speed", 150)
    # Use hardcoded Gemini API key from backend
    gemini_key = GEMINI_API_KEY
    
    if uploaded_file:
        previous_name = st.session_state.get("current_pdf_name")
        if previous_name != uploaded_file.name:
            st.session_state.pop("raw_text", None)
            st.session_state.pop("simplified_text", None)
        if "raw_text" not in st.session_state:
            try:
                uploaded_file.seek(0)
                st.session_state["raw_text"] = pdf_utils.extract_text_from_pdf(
                    uploaded_file
                )
                st.session_state["current_pdf_name"] = uploaded_file.name
            except RuntimeError as err:
                st.error(str(err))
    else:
        st.info("Upload a PDF file from the sidebar to begin reading.")
        return
    
    raw_text = st.session_state.get("raw_text", "")
    if not raw_text:
        return
    
    # View Mode Selection
    st.markdown("### View Options")
    view_mode = st.radio(
        "Choose text view:",
        ["Original", "Simplified"],
        horizontal=True,
        help="Original shows the text as-is. Simplified uses AI to make it easier to read.",
    )
    
    # Text Processing
    display_text = raw_text
    if view_mode == "Simplified":
        simplified_text = st.session_state.get("simplified_text")
        if not simplified_text:
            with st.spinner("Simplifying text..."):
                try:
                    simplified_text = simplify_text.simplify_text(
                        raw_text, gemini_key
                    )
                    st.session_state["simplified_text"] = simplified_text
                except Exception as err:  # pragma: no cover - UX guard
                    st.error(f"Unable to simplify text: {err}")
                    simplified_text = ""
        if simplified_text:
            display_text = simplified_text
    
    # Display Text
    st.markdown("### Reading Content")
    st.caption(f"Currently viewing: **{view_mode.lower()}** text")
    
    # Text Area
    st.text_area(
        "Reader Output",
        value=display_text,
        height=500,
        key=f"reader_output_{view_mode}",
        help="The text content from your PDF. You can scroll through it here.",
    )
    
    # Read Aloud Button
    if st.button("🔊 Read Aloud"):
        with st.spinner("Starting text-to-speech..."):
            try:
                segments = tts_module.speak_text(display_text, rate=highlight_speed)
                st.success(
                    f"Playing audio. Estimated {len(segments)} sentence segments."
                )
            except Exception as err:  # pragma: no cover - UX guard
                st.error(f"Unable to start speech: {err}")


# ============================================================================
# QUIZ TAB
# ============================================================================

def _render_quiz_tab(state: Dict[str, Any]) -> None:
    """Render the quiz practice tab with improved UI."""
    st.markdown("## 📝 Quiz Practice")
    
    raw_text = st.session_state.get("raw_text", "")
    # Use OpenAI key if provided, otherwise fallback to Gemini
    openai_key = state.get("openai_key")
    api_key = openai_key if openai_key else GEMINI_API_KEY
    
    # Validation
    disabled_reason = None
    if not raw_text:
        disabled_reason = "Upload a PDF first."
    
    # Generate Quiz Button
    if st.button(
        "🎯 Generate Quiz",
        disabled=disabled_reason is not None,
        help=disabled_reason or "Creates a quiz from your uploaded PDF content.",
    ):
        with st.spinner("Generating quiz..."):
            try:
                quiz = quiz_generator.generate_quiz(raw_text, api_key)
                st.session_state["current_quiz"] = quiz
                st.session_state["quiz_score"] = None
                st.success("Quiz generated successfully!")
            except Exception as err:  # pragma: no cover - UX guard
                st.error(f"Unable to generate quiz: {err}")
    
    # Display Quiz
    quiz = st.session_state.get("current_quiz", {})
    mcq_list = quiz.get("mcq", []) if isinstance(quiz, dict) else []
    
    if mcq_list:
        st.markdown("### Multiple Choice Questions")
        responses = {}
        for idx, item in enumerate(mcq_list):
            question = item.get("q", f"Question {idx + 1}")
            options = item.get("options", [])
            
            # Render question in a styled container
            st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
            st.markdown(f"**Question {idx + 1}**")
            responses[idx] = st.radio(
                question,
                options=options or ["Option A"],
                key=f"quiz_mcq_{idx}",
                label_visibility="collapsed",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit Button
        if st.button("✅ Submit Quiz"):
            total = len(mcq_list)
            correct = 0
            for idx, item in enumerate(mcq_list):
                answer = item.get("answer")
                if responses.get(idx) == answer:
                    correct += 1
            score = int((correct / total) * 100) if total else 0
            st.session_state["quiz_score"] = score
            database.save_quiz_result("demo_user", score)
            st.success(f"Score: {score}% ({correct}/{total} correct)")
    
    # Score Display
    if st.session_state.get("quiz_score") is not None:
        st.info(f"Latest quiz score: **{st.session_state['quiz_score']}%**")
    
    # Help Text
    if disabled_reason:
        st.caption(disabled_reason)
    elif not mcq_list:
        st.caption("Generate a quiz to see questions here.")


# ============================================================================
# PROGRESS TAB
# ============================================================================

def _build_heatmap(dates: List[str], theme: str) -> None:
    """Build and display the reading activity heatmap with theme-aware colors."""
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    if df.empty:
        return
    df["value"] = 1
    df["week"] = df["date"].dt.strftime("W%V")
    df["weekday"] = df["date"].dt.strftime("%a")
    df = df.sort_values("date")
    
    # Theme-aware color scale
    color_scale = "Blues" if theme == "Light" else "Bluyl"
    
    fig = px.density_heatmap(
        df,
        x="week",
        y="weekday",
        z="value",
        color_continuous_scale=color_scale,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Week",
        yaxis_title="Day",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width='stretch')


def _render_progress_tab(theme: str) -> None:
    """Render the progress dashboard tab with improved UI."""
    st.markdown("## 📊 Progress Dashboard")
    
    progress = database.get_progress("demo_user")
    sessions = progress.get("sessions", [])
    quizzes = progress.get("quizzes", [])
    
    if not sessions:
        today = date.today()
        sessions = [
            {"level": "combined", "timestamp": str(today - timedelta(days=i))}
            for i in range(5)
        ]
        st.caption("Showing demo data until sessions are logged.")
    
    session_dates = [
        str(item["timestamp"]).split(" ")[0] for item in sessions if item.get("timestamp")
    ]
    if not session_dates:
        session_dates = [str(date.today() - timedelta(days=i)) for i in range(5)]
    
    streak_info = gamification.calculate_streak(session_dates)
    streak_days = streak_info.get("streak", 0)
    
    if not quizzes:
        quizzes = [{"score": 80}]
        st.caption("No quiz history yet. Displaying default values.")
    
    # Calculate points
    total_points = 0
    for quiz in quizzes:
        score = float(quiz.get("score", 0))
        total_points += gamification.award_points(score, reading_time=0)["points"]
    
    last_quiz_score = float(quizzes[0].get("score", 0))
    badges = gamification.get_badges(total_points, streak_days).get("badge", "")
    
    # Metrics Display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Points", total_points)
    with col2:
        st.metric("Last Quiz Score", f"{last_quiz_score:.0f}%")
    with col3:
        st.metric("Streak Days", streak_days)
    
    # Badges
    if badges:
        st.success(f"Badges: {badges}")
    
    # Heatmap
    st.markdown("### Reading Activity")
    st.caption("Your reading activity over time")
    _build_heatmap(session_dates, theme)


# ============================================================================
# MAIN TABS
# ============================================================================

def main_tabs(state: Dict[str, Any]) -> None:
    """Create and render the main tab interface."""
    reader_tab, quiz_tab, progress_tab = st.tabs(
        ["📖 Reader", "📝 Quiz", "📊 Progress"]
    )
    
    with reader_tab:
        _render_reader_tab(state)
    
    with quiz_tab:
        _render_quiz_tab(state)
    
    with progress_tab:
        _render_progress_tab(state.get("theme", "Light"))


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main() -> None:
    """Main application entry point."""
    # Initialize
    init_page()
    database.init_db()
    
    # Get sidebar state (includes role and theme selection)
    sidebar_state = sidebar_layout()
    
    # Get selected role and theme, then inject appropriate CSS
    role = sidebar_state.get("role", "ADHD")
    theme = sidebar_state.get("theme", "Light")
    inject_css(role, theme)
    
    # Main title and description
    st.title("🧠 NeuroLearn")
    st.markdown(
        """
        **Your accessible learning hub for neurodivergent students.**
        
        Upload PDFs, simplify text, listen along, take quizzes, and track your progress.
        The interface adapts to your selected learning mode and theme for the best experience.
        """
    )
    
    # Render main tabs
    main_tabs(sidebar_state)


if __name__ == "__main__":
    main()
