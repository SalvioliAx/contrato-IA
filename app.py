import streamlit as st
import sys
import os

# Adiciona o diretório raiz do projeto ao início do sys.path
# para garantir que os módulos locais como 'config' sejam encontrados primeiro.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.utils import manage_api_key, initialize_embeddings
from ui.sidebar import render_sidebar
from ui.tabs import chat_tab, dashboard_tab, summary_tab, risks_tab, deadlines_tab, compliance_tab, anomalies_tab

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ContratIA", page_icon="💡")
hide_streamlit_style = "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>"
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("💡 ContratIA")

def main():
    """Função principal para executar a aplicação Streamlit."""
    # --- CHAVE DE API & EMBEDDINGS ---
    # Gerencia a chave de API e inicializa o modelo de embeddings uma vez.
    google_api_key = manage_api_key()
    if google_api_key:
        initialize_embeddings()

    # --- BARRA LATERAL (SIDEBAR) ---
    # A barra lateral gerencia o upload de documentos e o carregamento de coleções.
    # Ela atualiza o estado da sessão com base nas ações do usuário.
    render_sidebar()

    # --- ABAS DE CONTEÚDO PRINCIPAL ---
    # Verifica se os componentes necessários estão prontos para renderizar as abas.
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

    # --- DEFINE AS ABAS ---
    tab_chat, tab_dashboard, tab_resumo, tab_riscos, tab_prazos, tab_conformidade, tab_anomalias_tab = st.tabs([
        "💬 Chat", "📈 Dashboard", "📜 Resumo", "🚩 Riscos", "🗓️ Prazos", "⚖️ Conformidade", "📊 Anomalias"
    ])

    # --- RENDERIZA AS ABAS ---
    with tab_chat:
        chat.render()
    with tab_dashboard:
        dashboard.render()
    with tab_resumo:
        summary.render()
    with tab_riscos:
        risks.render()
    with tab_prazos:
        deadlines.render()
    with tab_conformidade:
        compliance.render()
    with tab_anomalias_tab:
        anomalies.render()

if __name__ == "__main__":
    # Inicializa chaves do estado da sessão se não existirem
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    main()


