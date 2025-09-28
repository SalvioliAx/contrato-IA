import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao caminho do Python para permitir importações absolutas
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Importação dos módulos completos para evitar erros de importação circular
from src.config import configure_page, initialize_session_state, get_api_key
from src.localization import Localization
from src.ui import sidebar
from src.services import document_processor

# Importação específica das funções de renderização das abas
from src.ui.tabs.chat_tab import display_chat_tab
from src.ui.tabs.dashboard_tab import display_dashboard_tab
from src.ui.tabs.summary_tab import display_summary_tab
from src.ui.tabs.risk_tab import display_risk_tab
from src.ui.tabs.deadline_tab import display_deadline_tab
from src.ui.tabs.compliance_tab import display_compliance_tab
from src.ui.tabs.anomaly_tab import display_anomaly_tab

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    # --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
    configure_page()
    initialize_session_state()

    # Inicializa o gestor de localização
    if "localization" not in st.session_state:
        st.session_state.localization = Localization()
    
    # Cria o layout do cabeçalho para o título e os botões de idioma
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💡 ContratIA")
    
    with col2:
        # Botões de idioma com layout horizontal
        lang_cols = st.columns(3)
        with lang_cols[0]:
            if st.button("🇧🇷 PT", use_container_width=True):
                st.session_state.language = "pt"
                st.rerun()
        with lang_cols[1]:
            if st.button("🇺🇸 EN", use_container_width=True):
                st.session_state.language = "en"
                st.rerun()
        with lang_cols[2]:
            if st.button("🇪🇸 ES", use_container_width=True):
                st.session_state.language = "es"
                st.rerun()

    # Define o idioma com base na seleção e obtém a função de tradução
    st.session_state.localization.set_language(st.session_state.get("language", "pt"))
    t = st.session_state.localization.get_translator()

    # --- 2. GESTÃO DA API KEY E MODELO DE EMBEDDINGS ---
    google_api_key = get_api_key(t)
    embeddings_initialized = False
    initialization_error = None

    if google_api_key and not st.session_state.embeddings_model:
        try:
            # CORREÇÃO: Chama a função a partir do módulo importado
            st.session_state.embeddings_model = document_processor.get_embeddings_model()
            embeddings_initialized = True
        except Exception as e:
            initialization_error = e
    elif st.session_state.embeddings_model:
        embeddings_initialized = True

    # Renderiza a barra lateral
    # CORREÇÃO: Chama a função a partir do módulo importado
    sidebar.display_sidebar(google_api_key, st.session_state.embeddings_model, t)

    # --- 3. LÓGICA DE EXIBIÇÃO DO CONTEÚDO PRINCIPAL ---
    if initialization_error:
        st.error(t("errors.embedding_initialization_failed", error=str(initialization_error)))
    elif not google_api_key or not embeddings_initialized:
        st.error(t("errors.api_key_or_embeddings_not_configured"))
    else:
        # Define as abas da aplicação usando os textos traduzidos
        tab_keys = ["chat", "dashboard", "summary", "risks", "deadlines", "compliance", "anomalies"]
        tab_titles = [t(f"tabs.{key}") for key in tab_keys]
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

        with tab1:
            display_chat_tab(t)
        with tab2:
            display_dashboard_tab(t)
        with tab3:
            display_summary_tab(t)
        with tab4:
            display_risk_tab(t)
        with tab5:
            display_deadline_tab(t)
        with tab6:
            display_compliance_tab(t)
        with tab7:
            display_anomaly_tab(t)

if __name__ == "__main__":
    main()

