import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um ficheiro .env (opcional, bom para desenvolvimento local)
load_dotenv()

# --- CONSTANTES GLOBAIS ---
COLECOES_DIR = Path("colecoes_ia")
COLECOES_DIR.mkdir(exist_ok=True)

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
def configure_page():
    """Define a configuração inicial da página Streamlit."""
    st.set_page_config(
        layout="wide",
        page_title="ContratIA",
        page_icon="💡"
    )
    # Esconde o menu do Streamlit e o rodapé para um visual mais limpo
    hide_streamlit_style = "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>"
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- GESTÃO DO ESTADO DA SESSÃO ---
def initialize_session_state():
    """Inicializa todas as chaves necessárias no estado da sessão do Streamlit."""
    # Mapeamento de chave -> valor padrão
    default_state = {
        "messages": [],
        "vector_store": None,
        "nomes_arquivos": None,
        "arquivos_pdf_originais": None,
        "colecao_ativa": None,
        "df_dashboard": None,
        "resumo_gerado": None,
        "arquivo_resumido": None,
        "analise_riscos_resultados": None,
        "eventos_contratuais_df": None,
        "conformidade_resultados": None,
        "anomalias_resultados": None,
        "language": "pt", # Idioma padrão
        "api_key_input": None,
        "embeddings_model": None,
        "localization": None
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --- GESTÃO DA CHAVE DE API ---
def get_api_key():
    """
    Obtém a chave de API do Google, priorizando os secrets do Streamlit,
    depois variáveis de ambiente e, por último, o input do utilizador.
    """
    # Tenta obter dos secrets do Streamlit (ideal para deploy)
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key
    except (KeyError, FileNotFoundError):
        pass

    # Tenta obter das variáveis de ambiente (bom para desenvolvimento)
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key

    # Como último recurso, pede ao utilizador na barra lateral
    # O input real está na UI (sidebar.py), aqui apenas recuperamos o valor
    if st.session_state.get("api_key_input"):
        google_api_key = st.session_state.api_key_input
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key

    return None
