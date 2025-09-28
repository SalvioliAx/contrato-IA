import streamlit as st
from pathlib import Path

# Importação dos componentes da nova estrutura
from src.config import initialize_session_state, configure_page, get_api_key
from src.localization import Localization
from src.ui.sidebar import render_sidebar
from src.ui.tabs import chat_tab, dashboard_tab, summary_tab, risk_tab, deadline_tab, compliance_tab, anomaly_tab
from src.services.document_processor import get_embeddings_model

# --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---

# Define o layout da página e o ícone
# Esta função deve ser a primeira chamada do Streamlit
configure_page()

# Inicializa as variáveis no st.session_state se ainda não existirem
initialize_session_state()

# Carrega a classe de localização e a armazena no estado da sessão
if "localization" not in st.session_state:
    st.session_state.localization = Localization()

# Define o idioma com base na seleção do utilizador (o padrão é 'pt')
st.session_state.localization.set_language(st.session_state.get("language", "pt"))
t = st.session_state.localization.get_translator()

# --- 2. GESTÃO DA API KEY E MODELO DE EMBEDDINGS ---

# Pede a chave de API (seja dos secrets ou por input) e a configura
google_api_key = get_api_key()

# Carrega o modelo de embeddings uma vez e o armazena no estado da sessão
if "embeddings_model" not in st.session_state:
    st.session_state.embeddings_model = get_embeddings_model(google_api_key)

# --- 3. RENDERIZAÇÃO DA INTERFACE ---

st.title("💡 ContratIA")

# Renderiza a barra lateral e obtém o estado dela (se os documentos foram processados)
render_sidebar(google_api_key, st.session_state.embeddings_model, t)

# Define as abas da aplicação usando os textos traduzidos
tab_keys = ["chat", "dashboard", "summary", "risks", "deadlines", "compliance", "anomalies"]
tab_titles = [t(f"tabs.{key}") for key in tab_keys]

tabs = st.tabs(tab_titles)
tab_map = dict(zip(tab_keys, tabs))

# Verifica se a API e os documentos estão prontos para uso
api_ready = google_api_key and st.session_state.embeddings_model
docs_ready = st.session_state.get("vector_store") is not None

if not api_ready:
    st.error(t("errors.api_key_or_embeddings_not_configured"))
elif not docs_ready:
    st.info(t("info.upload_documents_to_start"))
else:
    # --- 4. LÓGICA E RENDERIZAÇÃO DAS ABAS ---
    # Cada aba agora é uma chamada de função para o seu respectivo módulo

    with tab_map["chat"]:
        chat_tab.render(t)

    with tab_map["dashboard"]:
        dashboard_tab.render(t)

    with tab_map["summary"]:
        summary_tab.render(google_api_key, t)

    with tab_map["risks"]:
        risk_tab.render(google_api_key, t)

    with tab_map["deadlines"]:
        deadline_tab.render(google_api_key, t)

    with tab_map["compliance"]:
        compliance_tab.render(google_api_key, t)

    with tab_map["anomalies"]:
        anomaly_tab.render(t)

