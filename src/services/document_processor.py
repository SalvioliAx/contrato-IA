import streamlit as st
import os
import time
import base64
from pathlib import Path
import fitz  # PyMuPDF

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

def get_embeddings_model(api_key: str):
    """
    Inicializa e retorna o modelo de embeddings da Google.
    """
    if not api_key:
        raise ValueError("A chave de API não foi fornecida.")
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

@st.cache_resource(show_spinner=False)
def obter_vector_store_de_uploads(_lista_arquivos_pdf_upload, _embeddings_obj, api_key, _t):
    """
    Processa ficheiros PDF carregados para criar um vector store FAISS.
    """
    if not _lista_arquivos_pdf_upload or not api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []
    
    llm_vision = None
    if api_key:
        try:
            # ATUALIZAÇÃO: Alterado o nome do modelo para uma versão estável
            llm_vision = ChatGoogleGenerativeAI(model="gemini-pro-vision", temperature=0.1, request_timeout=300)
        except Exception as e:
            st.warning(f"Não foi possível inicializar o modelo de visão do Gemini: {e}")

    for arquivo_pdf_upload in _lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_pdf_upload.name
        st.info(_t("info.processing_file", filename=nome_arquivo))
        texto_extraido = False
        documentos_arquivo_atual = []

        # ... (lógica de extração de texto com PyPDF, PyMuPDF) ...

        # Tentativa com Gemini Vision
        if not texto_extraido and llm_vision:
            try:
                # ... (lógica de extração com Gemini Vision) ...
                pass
            except Exception as e_gemini:
                st.error(f"Erro no Gemini Vision para {nome_arquivo}: {e_gemini}")
    
    if not documentos_totais:
        return None, []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    docs_fragmentados = text_splitter.split_documents(documentos_totais)

    if not docs_fragmentados:
        return None, nomes_arquivos_processados

    vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
    return vector_store, nomes_arquivos_processados

