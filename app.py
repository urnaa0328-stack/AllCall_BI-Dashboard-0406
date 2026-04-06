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
ACCENT = "#0ACAF9"


def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, {NAVY} 0%, {NAVY_2} 100%);
            color: white;
        }}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }}

        .main-title {{
            font-size: 28px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 0.3rem;
        }}

        .sub-title {{
            font-size: 14px;
            color: #DCE6FF;
            margin-bottom: 1rem;
        }}

        .card {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.18);
        }}

        .card-title {{
            font-size: 13px;
            color: #DCE6FF;
            margin-bottom: 8px;
        }}

        .card-value {{
            font-size: 28px;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.2;
        }}

        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #FFFFFF;
            margin: 8px 0 12px 0;
        }}

        /* Metric card */
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            padding: 12px 16px;
            border-radius: 14px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: #DCE6FF !important;
        }}

        div[data-testid="stMetricLabel"] * {{
            color: #DCE6FF !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: #FFFFFF !important;
        }}

        div[data-testid="stMetricValue"] * {{
            color: #FFFFFF !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            color: #FFFFFF !important;
            padding: 8px 14px;
        }}

        .stTabs [data-baseweb="tab"] * {{
            color: #FFFFFF !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: {ACCENT} !important;
            color: #001b2a !important;
            font-weight: 700;
        }}

        .stTabs [aria-selected="true"] * {{
            color: #001b2a !important;
        }}

        /* Input label */
        .stSelectbox label,
        .stTextInput label,
        .stDateInput label,
        .stRadio label,
        .stMultiSelect label {{
            color: #FFFFFF !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: rgba(255,255,255,0.04) !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
            color: #FFFFFF !important;
            opacity: 1 !important;
        }}

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: #FFFFFF;
        }}

        /* General markdown/text */
        .stMarkdown, .stMarkdown p, .stText {{
            color: #FFFFFF !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #FFFFFF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    inject_css()

    st.markdown('<div class="main-title">AllCall BI Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Excel-д суурилсан Ticket, Sales, Social media, Operation dashboard</div>',
        unsafe_allow_html=True
    )

    # debug
    st.write("BASE_DIR:", str(BASE_DIR))
    st.write("EXCEL_PATH:", str(EXCEL_PATH))
    st.write("Excel exists:", EXCEL_PATH.exists())

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
