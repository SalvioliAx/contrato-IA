import streamlit as st

# Importações dos módulos da aplicação
from src.config import configure_page, initialize_session_state, get_api_key
from src.localization import Localization
from src.sidebar import display_sidebar
from src.services import document_processor

# Importações das abas da UI
from src.ui import chat_tab, dashboard_tab, summary_tab, risk_tab, deadline_tab, compliance_tab, anomaly_tab

def main():
    """
    Função principal que orquestra a aplicação Streamlit ContratIA.
    """
    # 1. Configuração inicial da página e do estado
    configure_page()
    initialize_session_state()

    # 2. Configuração da localização e tradução
    # (Assume que o idioma é gerido no session_state, inicializado em config.py)
    loc = Localization(default_lang=st.session_state.get("language", "pt"))
    # Language switching logic can be added to the sidebar if needed
    # loc.set_language(st.session_state.language)
    t = loc.get_translator()

    # 3. Gestão da Chave de API e Modelos
    api_key = get_api_key(t)
    
    # Inicializa o modelo de embeddings apenas se a chave estiver disponível
    if api_key and not st.session_state.get("embeddings_model"):
        try:
            st.session_state.embeddings_model = document_processor.get_embeddings_model(api_key)
        except ValueError as e:
            st.sidebar.error(f"{t('errors.embedding_init_failed')}: {e}")
            st.session_state.embeddings_model = None
            
    embeddings_model = st.session_state.get("embeddings_model")

    # 4. Renderizar a Barra Lateral
    display_sidebar(api_key, embeddings_model, t)

    # 5. Lógica do Layout Principal (Abas)
    st.title("💡 ContratIA")

    # Verifica se os pré-requisitos para as abas funcionarem estão carregados
    documentos_prontos = api_key and embeddings_model and st.session_state.get("vector_store") is not None

    if not (api_key and embeddings_model):
        st.error(t("errors.api_key_or_embeddings_not_configured_full"))
    elif not documentos_prontos:
        st.info(t("info.load_docs_to_enable_features"))
    else:
        # Cria as abas
        tab_chat, tab_dashboard, tab_resumo, tab_riscos, tab_prazos, tab_conformidade, tab_anomalias = st.tabs([
            t("tabs.chat"), t("tabs.dashboard"), t("tabs.summary"), t("tabs.risks"),
            t("tabs.deadlines"), t("tabs.compliance"), t("tabs.anomalies")
        ])

        # Renderiza o conteúdo de cada aba
        with tab_chat:
            chat_tab.display_chat_tab(t)
        with tab_dashboard:
            dashboard_tab.display_dashboard_tab(t)
        with tab_resumo:
            summary_tab.display_summary_tab(t)
        with tab_riscos:
            risk_tab.display_risk_tab(t)
        with tab_prazos:
            deadline_tab.display_deadline_tab(t)
        with tab_conformidade:
            compliance_tab.display_compliance_tab(t)
        with tab_anomalias:
            anomaly_tab.display_anomaly_tab(t)

if __name__ == "__main__":
    main()
