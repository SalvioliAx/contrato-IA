import os
import time
import base64
import streamlit as st
from pathlib import Path
import fitz  # PyMuPDF

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

@st.cache_resource(show_spinner=False)
def get_embeddings_model(api_key):
    """
    Carrega e armazena em cache o modelo de embeddings.
    Retorna None se a chave de API não for válida.
    """
    if not api_key:
        return None
    try:
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar embeddings: {e}")
        return None

def _extrair_texto_com_gemini(pdf_bytes, nome_arquivo, llm_vision, t):
    """Função auxiliar para extrair texto de um PDF usando o Gemini Vision."""
    documentos_gemini = []
    texto_extraido = False
    try:
        doc_fitz = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(doc_fitz)):
            page_obj = doc_fitz.load_page(page_num)
            pix = page_obj.get_pixmap(dpi=300) # Alta resolução para melhor OCR
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')

            human_message = HumanMessage(
                content=[
                    {"type": "text", "text": t("prompts.gemini_ocr.prompt")},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                ]
            )
            
            with st.spinner(t("info.gemini_processing_page", page=page_num + 1, total=len(doc_fitz), file=nome_arquivo)):
                ai_msg = llm_vision.invoke([human_message])
            
            if isinstance(ai_msg, AIMessage) and ai_msg.content and isinstance(ai_msg.content, str):
                texto_pagina = ai_msg.content
                if texto_pagina.strip():
                    doc = Document(page_content=texto_pagina, metadata={"source": nome_arquivo, "page": page_num, "method": "gemini_vision"})
                    documentos_gemini.append(doc)
                    texto_extraido = True
            time.sleep(2) # Respeitar limites da API

        doc_fitz.close()
        if texto_extraido:
            st.success(t("success.text_extracted_gemini", file=nome_arquivo))
    except Exception as e:
        st.error(t("errors.gemini_vision_error", file=nome_arquivo, error=str(e)[:200]))

    return documentos_gemini, texto_extraido


@st.cache_resource(show_spinner="Analisando documentos para busca e chat...")
def obter_vector_store_de_uploads(lista_arquivos_pdf_upload, _embeddings_obj, api_key, t):
    """
    Processa uma lista de arquivos PDF, extrai texto usando múltiplos métodos (fallback)
    e cria um Vector Store FAISS.
    """
    if not lista_arquivos_pdf_upload or not api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []
    llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=300)

    for arquivo_upload in lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_upload.name
        st.info(t("info.processing_file", file=nome_arquivo))
        
        documentos_arquivo = []
        sucesso = False
        temp_file_path = Path(f"temp_{nome_arquivo}")

        try:
            # Salva temporariamente para uso pelas bibliotecas
            with open(temp_file_path, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            # Tentativa 1: PyPDFLoader
            try:
                loader = PyPDFLoader(str(temp_file_path))
                pages = loader.load()
                if any(p.page_content and p.page_content.strip() for p in pages):
                    for p in pages:
                        p.metadata["method"] = "pypdf"
                    documentos_arquivo.extend(pages)
                    sucesso = True
                    st.success(t("success.text_extracted_pypdf", file=nome_arquivo))
            except Exception:
                st.warning(t("warnings.pypdf_failed_fallback", file=nome_arquivo))

            # Tentativa 2: PyMuPDF (se o primeiro falhar)
            if not sucesso:
                try:
                    doc_fitz = fitz.open(str(temp_file_path))
                    for num_pagina, pagina in enumerate(doc_fitz):
                        texto = pagina.get_text("text")
                        if texto and texto.strip():
                            doc = Document(page_content=texto, metadata={"source": nome_arquivo, "page": num_pagina, "method": "pymupdf"})
                            documentos_arquivo.append(doc)
                    doc_fitz.close()
                    if documentos_arquivo:
                        sucesso = True
                        st.success(t("success.text_extracted_pymupdf", file=nome_arquivo))
                except Exception:
                    st.warning(t("warnings.pymupdf_failed_fallback", file=nome_arquivo))
            
            # Tentativa 3: Gemini Vision (se todos os outros falharem)
            if not sucesso and llm_vision:
                st.write(t("info.trying_gemini_vision", file=nome_arquivo))
                arquivo_upload.seek(0)
                pdf_bytes = arquivo_upload.read()
                docs_gemini, sucesso_gemini = _extrair_texto_com_gemini(pdf_bytes, nome_arquivo, llm_vision, t)
                if sucesso_gemini:
                    documentos_arquivo = docs_gemini
                    sucesso = True

            if sucesso and documentos_arquivo:
                documentos_totais.extend(documentos_arquivo)
                nomes_arquivos_processados.append(nome_arquivo)
            else:
                st.error(t("errors.text_extraction_failed", file=nome_arquivo))

        except Exception as e:
            st.error(t("errors.general_file_processing_error", file=nome_arquivo, error=e))
        finally:
            if temp_file_path.exists():
                os.remove(temp_file_path)

    if not documentos_totais:
        st.error(t("errors.no_text_extracted_from_any_doc"))
        return None, []

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        docs_fragmentados = text_splitter.split_documents(documentos_totais)
        
        if not docs_fragmentados:
             st.error(t("errors.text_splitting_failed"))
             return None, nomes_arquivos_processados

        st.info(t("info.creating_vector_store", chunks=len(docs_fragmentados), files=len(nomes_arquivos_processados)))
        vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
        st.success(t("success.vector_store_created"))
        return vector_store, nomes_arquivos_processados
    except Exception as e:
        st.error(t("errors.faiss_creation_error", error=e))
        return None, nomes_arquivos_processados
