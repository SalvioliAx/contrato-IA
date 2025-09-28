import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao caminho do Python para garantir que as importações funcionem
# corretamente quando o script é executado a partir do diretório raiz.
sys.path.append(str(Path(__file__).resolve().parent))

# Importações dos módulos da aplicação
from src.config import configure_page, initialize_session_state, get_api_key
from src.localization import Localization
from src.sidebar import display_sidebar
from src.services import document_processor

# Importações das abas da UI
from src.ui import (
    chat_tab, dashboard_tab, summary_tab, risk_tab,
    deadline_tab, compliance_tab, anomaly_tab
)

def main():
    """
    Função principal que orquestra a aplicação Streamlit ContratIA.
    """
    # 1. Configuração inicial da página e do estado da sessão
    configure_page()
    initialize_session_state()

    # 2. Configuração da localização e tradução
    loc = Localization(default_lang=st.session_state.get("language", "pt"))
    t = loc.get_translator()

    # 3. Gestão da Chave de API e do modelo de Embeddings
    api_key = get_api_key(t)
    
    # Inicializa o modelo de embeddings apenas se a chave estiver disponível e ele ainda não existir
    if api_key and not st.session_state.get("embeddings_model"):
        try:
            st.session_state.embeddings_model = document_processor.get_embeddings_model(api_key)
        except ValueError as e:
            st.sidebar.error(f"{t('errors.embedding_init_failed')}: {e}")
            st.session_state.embeddings_model = None
            
    embeddings_model = st.session_state.get("embeddings_model")

    # 4. Renderizar a Barra Lateral
    # A barra lateral lida com o upload, carregamento de coleções e salvamento
    display_sidebar(api_key, embeddings_model, t)

    # 5. Lógica do Layout Principal (Título e Abas)
    st.title("💡 ContratIA")

    # Verifica se os pré-requisitos para as abas funcionarem estão carregados
    documentos_prontos = api_key and embeddings_model and st.session_state.get("vector_store") is not None

    if not (api_key and embeddings_model):
        st.error(t("errors.api_key_or_embeddings_not_configured_full"))
    elif not documentos_prontos:
        st.info(t("info.load_docs_to_enable_features"))
    else:
        # Cria as abas se tudo estiver pronto
        tab_list = [
            t("tabs.chat"), t("tabs.dashboard"), t("tabs.summary"), t("tabs.risks"),
            t("tabs.deadlines"), t("tabs.compliance"), t("tabs.anomalies")
        ]
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_list)

        # Renderiza o conteúdo de cada aba, passando a função de tradução 't'
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
