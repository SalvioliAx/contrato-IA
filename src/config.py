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
        "embeddings_model": None
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --- GESTÃO DA CHAVE DE API ---
def get_api_key():
    """
    Obtém a chave de API do Google, priorizando os secrets do Streamlit,
    depois variáveis de ambiente e, por último, o input do utilizador.
    Valida se a chave encontrada não está vazia.
    """
    # --- INÍCIO DO CÓDIGO DE DEPURAÇÃO TEMPORÁRIO ---
    # Este bloco de código irá ajudá-lo a ver o que está nos secrets.
    # Pode removê-lo depois de resolver o problema.
    with st.expander("🔍 Informações de Depuração dos Secrets", expanded=True):
        st.warning("Esta mensagem é para depuração e deve ser removida mais tarde.")
        try:
            if not st.secrets:
                st.error("st.secrets está completamente vazio.")
            else:
                st.write("Secrets encontrados:", list(st.secrets.keys()))
                if "GOOGLE_API_KEY" in st.secrets:
                    st.success("A chave 'GOOGLE_API_KEY' foi encontrada nos secrets.")
                    key_value = st.secrets["GOOGLE_API_KEY"]
                    st.info(f"Comprimento da chave: {len(key_value)}")
                    if not key_value or not key_value.strip():
                        st.error("PROBLEMA: O valor da chave está vazio ou contém apenas espaços.")
                    else:
                        st.success("PARECE OK: O valor da chave não está vazio.")
                else:
                    st.error("PROBLEMA: A chave 'GOOGLE_API_KEY' NÃO foi encontrada. Verifique se há erros de digitação.")
        except Exception as e:
            st.error(f"Ocorreu uma exceção ao tentar ler os secrets: {e}")
    # --- FIM DO CÓDIGO DE DEPURAÇÃO ---


    # Tenta obter dos secrets do Streamlit (ideal para deploy)
    try:
        google_api_key = st.secrets.get("GOOGLE_API_KEY")
        if google_api_key and google_api_key.strip():
            os.environ["GOOGLE_API_KEY"] = google_api_key
            return google_api_key
    except Exception: # Captura qualquer erro potencial ao aceder aos secrets
        pass

    # Tenta obter das variáveis de ambiente (bom para desenvolvimento)
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key.strip():
        os.environ["GOOGLE_API_KEY"] = google_api_key
        return google_api_key

    # Como último recurso, pede ao utilizador na barra lateral
    if st.session_state.get("api_key_input"):
        google_api_key = st.session_state.api_key_input
        if google_api_key and google_api_key.strip():
            os.environ["GOOGLE_API_KEY"] = google_api_key
            return google_api_key

    return None

