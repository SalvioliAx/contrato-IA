import streamlit as st
import os
import fitz  # PyMuPDF
import time
import base64
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from config import EMBEDDING_MODEL, GEMINI_FLASH_MODEL

# --- GERENCIAMENTO DE API E MODELOS ---

def manage_api_key():
    """Gerencia a chave de API do Google, recuperando-a dos secrets ou da entrada do usuário."""
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.sidebar.warning("Chave de API do Google não configurada nos Secrets.")
        google_api_key = st.sidebar.text_input(
            "(OU) Cole sua Chave de API do Google aqui:",
            type="password",
            key="api_key_input_main"
        )

    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.session_state.google_api_key = google_api_key
        return google_api_key
    
    st.session_state.google_api_key = None
    return None

@st.cache_resource
def initialize_embeddings():
    """Inicializa e armazena em cache o modelo de embeddings."""
    if st.session_state.get("google_api_key"):
        try:
            embeddings_model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
            st.session_state.embeddings_model = embeddings_model
            return embeddings_model
        except Exception as e:
            st.sidebar.error(f"Erro ao inicializar embeddings: {e}")
            st.session_state.embeddings_model = None
            return None
    return None

@st.cache_resource
def get_llm(temperature=0.2, timeout=120):
    """Retorna uma instância em cache do modelo ChatGoogleGenerativeAI."""
    if not st.session_state.get("google_api_key"):
        st.error("Chave de API não configurada.")
        return None
    return ChatGoogleGenerativeAI(
        model=GEMINI_FLASH_MODEL,
        temperature=temperature,
        request_timeout=timeout
    )

# --- PROCESSAMENTO DE PDF E TEXTO ---

@st.cache_data(show_spinner="Lendo conteúdo do arquivo PDF...")
def get_full_text_from_pdf(uploaded_file):
    """
    Extrai o texto completo de um objeto UploadedFile usando PyMuPDF e, como fallback, Gemini Vision.
    Retorna o texto extraído como uma string.
    """
    if not uploaded_file:
        return ""
    
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    
    # Tenta PyMuPDF primeiro
    full_text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text() + "\n"
    except Exception as e:
        st.warning(f"PyMuPDF falhou ao extrair texto de {uploaded_file.name}: {e}. Tentando Gemini Vision.")
        full_text = ""

    # Fallback para Gemini Vision se PyMuPDF falhar ou retornar texto vazio
    if not full_text.strip():
        st.info(f"Usando Gemini Vision para extração de texto de {uploaded_file.name}...")
        llm_vision = get_llm(temperature=0.1)
        if not llm_vision:
            st.error("Não é possível usar o Gemini Vision sem um LLM configurado.")
            return ""

        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=200)
                    img_bytes_vision = pix.tobytes("png")
                    base64_image = base64.b64encode(img_bytes_vision).decode('utf-8')

                    msg = HumanMessage(content=[
                        {"type": "text", "text": "Extraia todo o texto visível desta página com precisão."},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                    ])
                    
                    with st.spinner(f"Gemini processando página {page_num + 1}/{len(doc)} de {uploaded_file.name}..."):
                        ai_msg = llm_vision.invoke([msg])
                    
                    if isinstance(ai_msg, AIMessage) and ai_msg.content:
                        full_text += str(ai_msg.content) + "\n\n"
                    time.sleep(1)
        except Exception as e_gemini:
            st.error(f"Gemini Vision falhou para {uploaded_file.name}: {e_gemini}")
            return ""

    return full_text

def format_chat_for_markdown(chat_history):
    """Formata o histórico do chat em uma string Markdown para download."""
    markdown_text = "# Histórico da Conversa com ContratIA\n\n"
    for message in chat_history:
        role = "Você" if message["role"] == "user" else "IA"
        markdown_text += f"## {role}:\n{message['content']}\n\n"
        if "sources" in message and message.get("sources"):
            markdown_text += "### Fontes:\n"
            for i, doc in enumerate(message["sources"]):
                source_info = doc.metadata.get('source', 'N/A')
                page_info = doc.metadata.get('page', 'N/A')
                content_preview = doc.page_content.replace('\n', ' ').strip()[:300]
                markdown_text += f"- **Fonte {i+1}** (Arquivo: `{source_info}`, Pág: {page_info}):\n  > {content_preview}...\n\n"
        markdown_text += "---\n\n"
    return markdown_text
