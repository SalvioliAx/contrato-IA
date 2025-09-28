import streamlit as st
import os
import json
import time
import base64
from pathlib import Path
import fitz  # PyMuPDF

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

from config import COLECOES_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from core.utils import get_llm

# --- GERENCIAMENTO DE COLEÇÕES ---
def list_saved_collections():
    """Lista os nomes das coleções de vetores salvas localmente."""
    if not COLECOES_DIR.exists():
        return []
    return [d.name for d in COLECOES_DIR.iterdir() if d.is_dir()]

def save_current_collection(collection_name, vector_store, file_names):
    """Salva o vector store e o manifesto de arquivos em um diretório."""
    if not collection_name.strip():
        st.error("Por favor, forneça um nome para a coleção.")
        return False
    collection_path = COLECOES_DIR / collection_name
    try:
        collection_path.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(collection_path / "faiss_index"))
        with open(collection_path / "manifest.json", "w") as f:
            json.dump(file_names, f)
        st.success(f"Coleção '{collection_name}' salva com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar coleção: {e}")
        return False

@st.cache_resource(show_spinner="Carregando coleção...")
def load_collection(collection_name, _embeddings_obj):
    """Carrega uma coleção de vetores salva localmente."""
    collection_path = COLECOES_DIR / collection_name
    index_path = collection_path / "faiss_index"
    manifest_path = collection_path / "manifest.json"

    if not index_path.exists() or not manifest_path.exists():
        st.error(f"Coleção '{collection_name}' está incompleta ou corrompida.")
        return None, None
    try:
        vector_store = FAISS.load_local(
            str(index_path),
            embeddings=_embeddings_obj,
            allow_dangerous_deserialization=True
        )
        with open(manifest_path, "r") as f:
            file_names = json.load(f)
        st.success(f"Coleção '{collection_name}' carregada!")
        return vector_store, file_names
    except Exception as e:
        st.error(f"Erro ao carregar coleção '{collection_name}': {e}")
        return None, None

# --- PROCESSAMENTO DE DOCUMENTOS E CRIAÇÃO DO VECTOR STORE ---

def _extract_text_with_fallback(pdf_upload):
    """Função interna para tentar diferentes métodos de extração de texto para um único PDF."""
    file_name = pdf_upload.name
    all_docs = []
    
    temp_file_path = Path(f"temp_{file_name}")
    with open(temp_file_path, "wb") as f:
        f.write(pdf_upload.getbuffer())
    
    # Método 1: PyMuPDF (geralmente o mais confiável)
    try:
        st.write(f"Tentando extração com PyMuPDF para {file_name}...")
        with fitz.open(str(temp_file_path)) as doc_fitz:
            for page_num, page in enumerate(doc_fitz):
                text = page.get_text("text")
                if text and text.strip():
                    all_docs.append(Document(page_content=text, metadata={"source": file_name, "page": page_num, "method": "pymupdf"}))
        if any(doc.page_content.strip() for doc in all_docs):
            st.success(f"Texto extraído com PyMuPDF para {file_name}.")
            os.remove(temp_file_path)
            return all_docs
    except Exception as e_fitz:
        st.warning(f"PyMuPDF falhou para {file_name}: {e_fitz}. Tentando outros métodos.")

    # Método 2: PyPDFLoader (como fallback)
    try:
        st.write(f"Tentando extração com PyPDFLoader para {file_name}...")
        loader = PyPDFLoader(str(temp_file_path))
        pages = loader.load()
        if pages and any(p.page_content.strip() for p in pages):
            for p in pages:
                p.metadata["method"] = "pypdf"
            st.success(f"Texto extraído com PyPDFLoader para {file_name}.")
            os.remove(temp_file_path)
            return pages
    except Exception as e_pypdf:
        st.warning(f"PyPDFLoader falhou para {file_name}: {e_pypdf}. Tentando Gemini Vision.")

    # Método 3: Gemini Vision (como último recurso)
    llm_vision = get_llm(temperature=0.1)
    if llm_vision:
        st.write(f"Tentando extração com Gemini Vision para {file_name}...")
        all_docs = []
        pdf_upload.seek(0)
        pdf_bytes = pdf_upload.read()
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_vision:
                for page_num in range(len(doc_vision)):
                    page = doc_vision.load_page(page_num)
                    pix = page.get_pixmap(dpi=300)
                    img_bytes = pix.tobytes("png")
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    msg = HumanMessage(content=[{"type": "text", "text": "Extraia todo o texto visível desta página."}, {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}])
                    
                    with st.spinner(f"Gemini processando página {page_num + 1}/{len(doc_vision)} de {file_name}..."):
                        ai_msg = llm_vision.invoke([msg])
                    
                    if isinstance(ai_msg, AIMessage) and ai_msg.content:
                        all_docs.append(Document(page_content=str(ai_msg.content), metadata={"source": file_name, "page": page_num, "method": "gemini_vision"}))
                    time.sleep(2)
            
            if any(doc.page_content.strip() for doc in all_docs):
                st.success(f"Texto extraído com Gemini Vision para {file_name}.")
                os.remove(temp_file_path)
                return all_docs
        except Exception as e_gemini:
            st.error(f"Gemini Vision falhou para {file_name}: {e_gemini}")
    
    if temp_file_path.exists():
        os.remove(temp_file_path)
    st.error(f"Falha ao extrair texto de {file_name} usando todos os métodos disponíveis.")
    return []

@st.cache_resource(show_spinner="Analisando documentos para habilitar busca e chat...")
def create_vector_store_from_uploads(pdf_uploads, _embeddings_obj):
    """Processa uma lista de arquivos PDF enviados e cria um vector store FAISS."""
    if not pdf_uploads or not st.session_state.get("google_api_key") or not _embeddings_obj:
        return None, None

    all_documents = []
    processed_file_names = []

    for pdf in pdf_uploads:
        st.info(f"Processando arquivo: {pdf.name}...")
        docs_from_file = _extract_text_with_fallback(pdf)
        if docs_from_file:
            all_documents.extend(docs_from_file)
            processed_file_names.append(pdf.name)
    
    if not all_documents:
        st.error("Nenhum texto pôde ser extraído de nenhum dos documentos fornecidos.")
        return None, []

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        split_docs = text_splitter.split_documents(all_documents)
        
        if not split_docs:
             st.error("A fragmentação do texto não resultou em nenhum documento. Verifique o conteúdo extraído.")
             return None, processed_file_names

        st.info(f"Criando vector store com {len(split_docs)} fragmentos de {len(processed_file_names)} arquivos.")
        vector_store = FAISS.from_documents(split_docs, _embeddings_obj)
        st.success("Vector store criado com sucesso!")
        return vector_store, processed_file_names
    except Exception as e_faiss:
        st.error(f"Falha ao criar o vector store FAISS: {e_faiss}")
        return None, processed_file_names
