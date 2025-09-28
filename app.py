import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao caminho do Python
# para garantir que as importações de 'src' funcionem corretamente.
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Importações locais do projeto
from src.config import configure_page, initialize_session_state, get_api_key
from src.localization import Localization
from src.ui.sidebar import display_sidebar  # Nome da função corrigido aqui
from src.ui.tabs import chat_tab, dashboard_tab, summary_tab, risk_tab, deadline_tab, compliance_tab, anomaly_tab

def main():
    """Função principal que executa a aplicação Streamlit."""
    # --- 1. CONFIGURAÇÃO INICIAL ---
    configure_page()
    initialize_session_state()

    # Inicializa o gestor de idiomas
    if "localization" not in st.session_state:
        st.session_state.localization = Localization()
    
    st.session_state.localization.set_language(st.session_state.get("language", "pt"))
    t = st.session_state.localization.get_translator()
    
    # --- Layout do Cabeçalho ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💡 ContratIA")
    with col2:
        btn_cols = st.columns(3)
        if btn_cols[0].button(t("language_selector_options.pt"), key="lang_pt", use_container_width=True):
            st.session_state.language = "pt"
            st.rerun()
        if btn_cols[1].button(t("language_selector_options.en"), key="lang_en", use_container_width=True):
            st.session_state.language = "en"
            st.rerun()
        if btn_cols[2].button(t("language_selector_options.es"), key="lang_es", use_container_width=True):
            st.session_state.language = "es"
            st.rerun()

    # --- 2. GESTÃO DA API KEY E MODELO DE EMBEDDINGS ---
    google_api_key = get_api_key()
    embeddings_initialized = False
    initialization_error = None

    if google_api_key:
        try:
            if not st.session_state.get("embeddings_model"):
                st.session_state.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            embeddings_initialized = True
        except Exception as e:
            initialization_error = e
            st.session_state.embeddings_model = None
    else:
        st.session_state.embeddings_model = None

    # --- 3. RENDERIZAÇÃO DA UI ---
    display_sidebar(t)  # Chamada da função com o nome corrigido
    
    tab_titles = [
        t("tabs.chat"), t("tabs.dashboard"), t("tabs.summary"), 
        t("tabs.risks"), t("tabs.deadlines"), t("tabs.compliance"), t("tabs.anomalies")
    ]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

    documentos_prontos = google_api_key and embeddings_initialized and st.session_state.get("vector_store") is not None

    if not (google_api_key and embeddings_initialized):
        st.error(t("errors.api_key_or_embeddings_not_configured"))
        if initialization_error:
            st.warning(f"{t('info.error_initializing_embeddings')}:")
            st.exception(initialization_error)
    elif not documentos_prontos:
        st.info(t("info.upload_documents_to_start"))
    else:
        with tab1:
            chat_tab.display_chat_tab(t)
        with tab2:
            dashboard_tab.display_dashboard_tab(t)
        with tab3:
            summary_tab.display_summary_tab(t)
        with tab4:
            risk_tab.display_risk_tab(t)
        with tab5:
            deadline_tab.display_deadline_tab(t)
        with tab6:
            compliance_tab.display_compliance_tab(t)
        with tab7:
            anomaly_tab.display_anomaly_tab(t)

if __name__ == "__main__":
    main()

