import streamlit as st
from core.config import get_google_api_key, hide_streamlit_style
from core.embeddings import init_embeddings
from ui.sidebar import render_sidebar
from ui.tabs.chat_tab import render_chat_tab
from ui.tabs.dashboard_tab import render_dashboard_tab
from ui.tabs.resumo_tab import render_resumo_tab
from ui.tabs.riscos_tab import render_riscos_tab
from ui.tabs.prazos_tab import render_prazos_tab
from ui.tabs.conformidade_tab import render_conformidade_tab
from ui.tabs.anomalias_tab import render_anomalias_tab

st.set_page_config(layout="wide", page_title="ContratIA", page_icon="💡")
hide_streamlit_style()
st.title("💡 ContratIA")

google_api_key = get_google_api_key()
embeddings_global = init_embeddings(google_api_key)

render_sidebar(embeddings_global, google_api_key)

abas = {
    "Chat": render_chat_tab,
    "Dashboard": render_dashboard_tab,
    "Resumo": render_resumo_tab,
    "Riscos": render_riscos_tab,
    "Prazos": render_prazos_tab,
    "Conformidade": render_conformidade_tab,
    "Anomalias": lambda g: render_anomalias_tab()
}

aba = st.tabs(list(abas.keys()))

for i, (nome, func) in enumerate(abas.items()):
    with aba[i]:
        func(google_api_key)
