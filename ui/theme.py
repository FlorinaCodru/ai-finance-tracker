import streamlit as st

def inject_theme():
    st.markdown(
        """
        <style>
          /* right sidebar + width */
          [data-testid="stAppViewContainer"] { order: 1; }
          [data-testid="stSidebar"] {
            order: 2; border-left: 1px solid #eee; border-right: none;
            width: 360px !important; min-width: 360px !important; max-width: 360px !important;
            flex: 0 0 360px !important;
          }
          [data-testid="stSidebar"] > div { width: 360px !important; }
          section[data-testid="stSidebarCollapsedControl"] { left: auto; right: 0; }

          :root {
            --brand-yellow: #facc15; --brand-yellow-dark: #eab308;
            --brand-yellow-faint: #fffbeb; --soft-border: #fde68a; --ink: #111827;
          }

          h1, .st-emotion-cache-10trblm, .st-emotion-cache-1wmy9hl {
            background: linear-gradient(90deg, #facc15, #f59e0b);
            -webkit-background-clip: text; background-clip: text; color: transparent;
          }

          .stButton > button, .stDownloadButton > button {
            background: var(--brand-yellow) !important;
            border: 1px solid var(--brand-yellow-dark) !important;
            color: var(--ink) !important; font-weight: 600 !important; border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(234,179,8,.25) !important;
          }
          .stButton > button:hover, .stDownloadButton > button:hover {
            filter: brightness(0.95) !important; background: #fbbf24 !important;
            border-color: var(--brand-yellow-dark) !important;
          }
          .stButton > button:active { transform: translateY(1px); }

          .stTabs [data-baseweb="tab-list"] { gap: 12px; }
          .stTabs [data-baseweb="tab"] { padding: 10px 16px; border-radius: 10px; background: #fff7cc; border: 1px solid var(--soft-border); }

          .metric-box { border:1px solid var(--soft-border); border-radius:12px; padding:16px; background: var(--brand-yellow-faint); box-shadow: 0 2px 10px rgba(234,179,8,.25); }
          .kpi-title { font-size:0.95rem; color:#6b7280; margin-bottom:4px;}
          .kpi-value { font-size:1.6rem; font-weight:700; }
          .good { color: #166534; font-weight: 600; } .bad { color: #b45309; font-weight: 600; } .neutral { color: #6b7280; font-weight: 600; }

          .enhanced-card { border:1px solid var(--soft-border); background: var(--brand-yellow-faint); border-radius:16px; padding:16px; box-shadow: 0 2px 12px rgba(234,179,8,.25); }
          .enhanced-card.padded { padding-top: 16px; padding-bottom: 16px;  margin: 20px 0;  }
         
           .section-title { font-weight:700; margin-bottom:6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
