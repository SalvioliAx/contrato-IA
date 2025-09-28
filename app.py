import sys
from pathlib import Path
import streamlit as st

# Adiciona o diretório 'src' ao caminho do Python para garantir que as importações funcionem
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Importação dos módulos da aplicação
from config import configure_page, initialize_session_state, get_api_key
from localization import Localization
from ui import sidebar
from services import document_processor
from ui.tabs import (
    chat_tab, dashboard_tab, summary_tab, risk_tab,
    deadline_tab, compliance_tab, anomaly_tab
)

def main():
    """Função principal que executa a aplicação Streamlit."""
    # --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
    configure_page()
    initialize_session_state()

    # Instancia e configura o localizador
    if "localization" not in st.session_state:
        st.session_state.localization = Localization()
    
    # Define o idioma com base na seleção do utilizador
    lang = st.session_state.get("language", "pt")
    st.session_state.localization.set_language(lang)
    t = st.session_state.localization.get_translator()

    # Layout do cabeçalho
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💡 ContratIA")
    with col2:
        cols = st.columns(3)
        with cols[0]:
            if st.button("🇧🇷 PT", use_container_width=True):
                st.session_state.language = "pt"
                st.rerun()
        with cols[1]:
            if st.button("🇺🇸 EN", use_container_width=True):
                st.session_state.language = "en"
                st.rerun()
        with cols[2]:
            if st.button("🇪🇸 ES", use_container_width=True):
                st.session_state.language = "es"
                st.rerun()

    # --- 2. GESTÃO DA API KEY E MODELO DE EMBEDDINGS ---
    google_api_key = get_api_key(t)
    embeddings_initialized = False
    initialization_error = None

    if google_api_key:
        try:
            st.session_state.embeddings_model = document_processor.get_embeddings_model(google_api_key)
            if st.session_state.embeddings_model:
                embeddings_initialized = True
        except Exception as e:
            # CORREÇÃO: Captura o erro e usa uma nova chave de tradução para uma mensagem mais detalhada
            print(f"ERRO DETALHADO DE INICIALIZAÇÃO: {e}") 
            initialization_error = t("errors.embedding_initialization_failed_detailed", error=str(e))
    else:
        initialization_error = t("errors.api_key_or_embeddings_not_configured")

    # Renderiza a barra lateral
    sidebar.display_sidebar(google_api_key, st.session_state.embeddings_model, t)

    # --- 3. LÓGICA DE EXIBIÇÃO DO CONTEÚDO PRINCIPAL ---
    if not embeddings_initialized:
        if initialization_error:
            st.error(initialization_error, icon="🚨")
        else:
            st.error(t("errors.api_key_or_embeddings_not_configured"), icon="🚨")
    elif not st.session_state.get("vector_store"):
        st.info(t("info.please_load_docs"))
    else:
        # Define as abas da aplicação
        tab_titles = [
            t("tabs.chat"), t("tabs.dashboard"), t("tabs.summary"), t("tabs.risks"),
            t("tabs.deadlines"), t("tabs.compliance"), t("tabs.anomalies")
        ]
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

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

