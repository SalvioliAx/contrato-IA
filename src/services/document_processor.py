import streamlit as st
import os
import time
import base64
import fitz  # PyMuPDF
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

@st.cache_resource(show_spinner=True)
def obter_vector_store_de_uploads(lista_arquivos_pdf_upload, _embeddings_obj, _t):
    """
    Processa uma lista de arquivos PDF, extrai texto usando múltiplos métodos,
    e cria um vector store FAISS.
    """
    if not lista_arquivos_pdf_upload or not _embeddings_obj:
        return None, []

    documentos_totais = []
    nomes_arquivos_processados = []
    llm_vision = None

    try:
        llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=300)
    except Exception as e:
        st.warning(_t("document_processor.warning_vision_model_failed", error=e))
        llm_vision = None

    for arquivo_pdf_upload in lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_pdf_upload.name
        st.info(_t("document_processor.info_processing_file", name=nome_arquivo))
        documentos_arquivo_atual, texto_extraido_com_sucesso = [], False
        temp_file_path = Path(f"temp_{nome_arquivo}")

        try:
            with open(temp_file_path, "wb") as f:
                f.write(arquivo_pdf_upload.getbuffer())

            # Tentativa 1: PyPDFLoader
            try:
                loader = PyPDFLoader(str(temp_file_path))
                pages_pypdf = loader.load()
                if pages_pypdf:
                    texto_concatenado = "".join(p.page_content for p in pages_pypdf if p.page_content)
                    if len(texto_concatenado.strip()) > 100:
                        documentos_arquivo_atual = [
                            Document(page_content=p.page_content, metadata={"source": nome_arquivo, "page": p.metadata.get("page", i), "method": "pypdf"})
                            for i, p in enumerate(pages_pypdf) if p.page_content and p.page_content.strip()
                        ]
                        st.success(_t("document_processor.success_pypdf", name=nome_arquivo))
                        texto_extraido_com_sucesso = True
            except Exception as e_pypdf:
                st.warning(_t("document_processor.warning_pypdf_failed", name=nome_arquivo, error=e_pypdf))

            # Tentativa 2: PyMuPDF (fitz)
            if not texto_extraido_com_sucesso:
                try:
                    documentos_arquivo_atual = []
                    with fitz.open(str(temp_file_path)) as doc_fitz:
                        texto_completo = ""
                        for num, page in enumerate(doc_fitz):
                            texto_pagina = page.get_text("text")
                            if texto_pagina and texto_pagina.strip():
                                texto_completo += texto_pagina
                                doc = Document(page_content=texto_pagina, metadata={"source": nome_arquivo, "page": num, "method": "pymupdf"})
                                documentos_arquivo_atual.append(doc)
                    if len(texto_completo.strip()) > 100:
                        st.success(_t("document_processor.success_pymupdf", name=nome_arquivo))
                        texto_extraido_com_sucesso = True
                except Exception as e_fitz:
                    st.warning(_t("document_processor.warning_pymupdf_failed", name=nome_arquivo, error=e_fitz))

            # Tentativa 3: Gemini Vision
            if not texto_extraido_com_sucesso and llm_vision:
                documentos_arquivo_atual = []
                try:
                    arquivo_pdf_upload.seek(0)
                    pdf_bytes = arquivo_pdf_upload.read()
                    prompt_gemini_ocr = _t("document_processor.prompt_gemini_ocr")
                    
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_vision:
                        for page_num in range(len(doc_fitz_vision)):
                            page_obj = doc_fitz_vision.load_page(page_num)
                            pix = page_obj.get_pixmap(dpi=300)
                            img_bytes = pix.tobytes("png")
                            base64_image = base64.b64encode(img_bytes).decode('utf-8')
                            
                            human_message = HumanMessage(content=[{"type": "text", "text": prompt_gemini_ocr}, {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}])
                            
                            spinner_text = _t("document_processor.spinner_gemini_processing", page=page_num + 1, total=len(doc_fitz_vision), name=nome_arquivo)
                            with st.spinner(spinner_text):
                                ai_msg = llm_vision.invoke([human_message])
                            
                            if isinstance(ai_msg, AIMessage) and ai_msg.content and isinstance(ai_msg.content, str):
                                texto_pagina_gemini = ai_msg.content
                                if texto_pagina_gemini.strip():
                                    doc = Document(page_content=texto_pagina_gemini, metadata={"source": nome_arquivo, "page": page_num, "method": "gemini_vision"})
                                    documentos_arquivo_atual.append(doc)
                                    texto_extraido_com_sucesso = True
                            time.sleep(2)
                    
                    if texto_extraido_com_sucesso:
                        st.success(_t("document_processor.success_gemini", name=nome_arquivo))
                    else:
                        st.warning(_t("document_processor.warning_gemini_no_text", name=nome_arquivo))
                except Exception as e_gemini:
                    st.error(_t("document_processor.error_gemini", name=nome_arquivo, error=str(e_gemini)[:200]))

            if texto_extraido_com_sucesso and documentos_arquivo_atual:
                documentos_totais.extend(documentos_arquivo_atual)
                nomes_arquivos_processados.append(nome_arquivo)
            else:
                st.error(_t("document_processor.error_no_text_extracted", name=nome_arquivo))

        except Exception as e_geral:
            st.error(_t("document_processor.error_general_processing", name=nome_arquivo, error=e_geral))
        finally:
            if temp_file_path.exists():
                try:
                    os.remove(temp_file_path)
                except OSError as e:
                    st.warning(f"Não foi possível remover o arquivo temporário {temp_file_path}: {e}")

    if not documentos_totais:
        st.error(_t("document_processor.error_no_text_from_any_doc"))
        return None, []

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        docs_fragmentados = text_splitter.split_documents(documentos_totais)
        
        if not docs_fragmentados:
            st.error(_t("document_processor.error_splitting_failed"))
            return None, nomes_arquivos_processados

        st.info(_t("document_processor.info_creating_vector_store", count=len(docs_fragmentados), files=len(nomes_arquivos_processados)))
        vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
        st.success(_t("document_processor.success_vector_store_created"))
        return vector_store, nomes_arquivos_processados
    except Exception as e_faiss:
        st.error(_t("document_processor.error_faiss_creation", error=e_faiss))
        return None, nomes_arquivos_processados

