from pathlib import Path
import os
import streamlit as st

# Diretório para salvar as coleções de vetores
COLECOES_DIR = Path("colecoes_ia")
COLECOES_DIR.mkdir(exist_ok=True)

# Função para obter a chave da API do Google
def get_google_api_key():
    """
    Obtém a chave da API do Google a partir dos secrets do Streamlit
    ou de um input na barra lateral como fallback.
    """
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key
    except (KeyError, FileNotFoundError):
        st.sidebar.warning("Chave de API do Google não configurada nos Secrets.")
        google_api_key = st.sidebar.text_input(
            "(OU) Cole sua Chave de API do Google aqui:",
            type="password",
            key="api_key_input_main"
        )
        if google_api_key:
            os.environ["GOOGLE_API_KEY"] = google_api_key
            return google_api_key
        return None

# Função para aplicar estilos CSS e ocultar elementos padrão do Streamlit
def hide_streamlit_style():
    """Aplica CSS para customizar a interface."""
    st.markdown(
        "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>",
        unsafe_allow_html=True,
    )
