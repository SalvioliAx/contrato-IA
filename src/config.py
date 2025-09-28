import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

# Carrega variáveis de ambiente de um ficheiro .env (opcional, bom para desenvolvimento local)
load_dotenv()

# --- CONSTANTES GLOBAIS ---
# Define o diretório onde as coleções de vetores serão salvas
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
    """Inicializa todas as chaves necessárias no estado da sessão do Streamlit se não existirem."""
    default_state = {
        "messages": [],
        "vector_store": None,
        "nomes_arquivos": None,
        "arquivos_pdf_originais": None,
        "colecao_ativa": None,
        "df_dashboard": pd.DataFrame(),
        "resumo_gerado": None,
        "arquivo_resumido": None,
        "analise_riscos_resultados": None,
        "eventos_contratuais_df": pd.DataFrame(),
        "conformidade_resultados": None,
        "anomalias_resultados": None,
        "language": "pt",
        "api_key_input": None,
        "embeddings_model": None
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --- GESTÃO DA CHAVE DE API ---
def get_api_key(t):
    """
    Obtém a chave de API do Google, priorizando os secrets do Streamlit,
    depois variáveis de ambiente e, por último, o input do utilizador.
    """
    # 1. Tenta obter dos secrets do Streamlit (ideal para deploy)
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        return api_key

    # 2. Tenta obter das variáveis de ambiente (bom para desenvolvimento local com .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        return api_key

    # 3. Como último recurso, usa o que foi inserido pelo utilizador na barra lateral
    # O input em si é gerido na UI (app.py ou sidebar.py), aqui apenas lemos o estado.
    if st.session_state.get("api_key_input"):
        api_key = st.session_state.api_key_input
        os.environ["GOOGLE_API_KEY"] = api_key
        return api_key
        
    # Se nenhuma das opções acima funcionar, pede ao utilizador na barra lateral.
    # Esta parte é mais declarativa, a UI principal deve renderizar o input.
    with st.sidebar:
        st.sidebar.warning(t("warnings.api_key_not_found"))
        api_key_input = st.sidebar.text_input(
            label=t("sidebar.api_key_input_label"),
            type="password",
            key="api_key_input_widget" # Chave única para o widget
        )
        if api_key_input:
            st.session_state.api_key_input = api_key_input
            os.environ["GOOGLE_API_KEY"] = api_key_input
            st.rerun() # Recarrega para aplicar a chave
            return api_key_input

    return None
