import streamlit as st
from pathlib import Path

from ticket_dashboard import render_ticket_dashboard
from social_dashboard import render_social_media_dashboard
from sales_dashboard import render_sales_dashboard
from operation_dashboard import render_operation_dashboard

st.set_page_config(
    page_title="AllCall BI Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "allcall_bi_data.xlsx"

NAVY = "#02013B"
NAVY_2 = "#060658"
BLUE = "#0D1691"
ACCENT = "#0ACAF9"
WHITE = "#FFFFFF"
SOFT_WHITE = "#EAF2FF"


def inject_css():
    st.markdown(
        f"""
        <style>
        /* Main app background */
        .stApp {{
            background: linear-gradient(180deg, {NAVY} 0%, {NAVY_2} 100%);
            color: {WHITE};
        }}

        /* Top white header area */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 0rem !important;
        }}

        [data-testid="stDecoration"] {{
            display: none !important;
        }}

        div[data-testid="stToolbar"] {{
            top: 0.5rem !important;
            right: 1rem !important;
        }}

        /* Layout */
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }}

        /* Titles */
        .main-title {{
            font-size: 32px;
            font-weight: 800;
            color: {WHITE};
            margin-bottom: 0.25rem;
        }}

        .sub-title {{
            font-size: 15px;
            color: {SOFT_WHITE};
            margin-bottom: 1.1rem;
        }}

        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: {WHITE};
            margin: 8px 0 12px 0;
        }}

        /* Custom cards */
        .card {{
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        }}

        .card-title {{
            font-size: 13px;
            color: {SOFT_WHITE} !important;
            font-weight: 600 !important;
            margin-bottom: 8px;
        }}

        .card-value {{
            font-size: 28px;
            font-weight: 800;
            color: {WHITE} !important;
            line-height: 1.2;
        }}

        /* Metric cards */
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.18);
            padding: 12px 16px;
            border-radius: 14px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {SOFT_WHITE} !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMetricLabel"] * {{
            color: {SOFT_WHITE} !important;
            opacity: 1 !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: {WHITE} !important;
            opacity: 1 !important;
        }}

        div[data-testid="stMetricValue"] * {{
            color: {WHITE} !important;
            opacity: 1 !important;
            font-weight: 800 !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            color: {WHITE} !important;
            padding: 8px 14px;
        }}

        .stTabs [data-baseweb="tab"] * {{
            color: {WHITE} !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: {ACCENT} !important;
            color: #001b2a !important;
            font-weight: 700;
        }}

        .stTabs [aria-selected="true"] * {{
            color: #001b2a !important;
        }}

        /* Inputs */
        .stSelectbox label,
        .stTextInput label,
        .stDateInput label,
        .stRadio label,
        .stMultiSelect label {{
            color: {WHITE} !important;
            font-weight: 600 !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.04) !important;
            border-right: 1px solid rgba(255,255,255,0.06);
        }}

        section[data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            color: {WHITE} !important;
        }}

        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
            color: {WHITE} !important;
            opacity: 1 !important;
        }}

        /* Markdown and headers */
        .stMarkdown, .stMarkdown p, .stText {{
            color: {WHITE} !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: {WHITE} !important;
        }}

        /* Tables / dataframes container feel */
        div[data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    inject_css()

    st.markdown(
        '<div class="main-title">AllCall BI Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-title">Excel-д суурилсан Ticket, Sales, Social media, Operation dashboard</div>',
        unsafe_allow_html=True
    )

    if not EXCEL_PATH.exists():
        st.error(f"Excel файл олдсонгүй: {EXCEL_PATH}")
        return

    menu = st.sidebar.radio(
        "Цэс",
        ["Ticket", "Sales", "Social media", "Operation"]
    )

    if menu == "Ticket":
        render_ticket_dashboard(str(EXCEL_PATH))
    elif menu == "Sales":
        render_sales_dashboard(str(EXCEL_PATH))
    elif menu == "Social media":
        render_social_media_dashboard(str(EXCEL_PATH))
    elif menu == "Operation":
        render_operation_dashboard(str(EXCEL_PATH))


if __name__ == "__main__":
    main()
