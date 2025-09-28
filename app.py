import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao path do Python para garantir que as importações
# como 'from core.utils...' funcionem em todos os módulos.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.utils import manage_api_key, initialize_embeddings
from ui.sidebar import render_sidebar

# Importação direta e explícita de cada módulo de aba
from ui.tabs import anomalies
from ui.tabs import chat
from ui.tabs import compliance
from ui.tabs import dashboard
from ui.tabs import deadlines
from ui.tabs import risks
from ui.tabs import summary


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ContratIA", page_icon="💡")
hide_streamlit_style = "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>"
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("💡 ContratIA")

def main():
    """Função principal para executar a aplicação Streamlit."""
    manage_api_key()
    initialize_embeddings()
    render_sidebar()

    documentos_prontos = (
        st.session_state.get("google_api_key")
        and st.session_state.get("embeddings_model")
        and st.session_state.get("vector_store")
    )

    if not documentos_prontos:
        if not st.session_state.get("google_api_key"):
            st.error("Chave de API do Google não está configurada. Verifique a barra lateral.")
        else:
            st.info("👈 Por favor, carregue e processe documentos PDF ou uma coleção existente na barra lateral para habilitar as funcionalidades.")
        return

    tab_definitions = {
        "💬 Chat": chat,
        "📈 Dashboard": dashboard,
        "📜 Resumo": summary,
        "🚩 Riscos": risks,
        "🗓️ Prazos": deadlines,
        "⚖️ Conformidade": compliance,
        "📊 Anomalias": anomalies,
    }
    
    tabs = st.tabs(tab_definitions.keys())

    for tab, (tab_name, tab_module) in zip(tabs, tab_definitions.items()):
        with tab:
            tab_module.render()


if __name__ == "__main__":
    if "messages" not in st.session_state:
        st.session_state.messages = []
    main()

