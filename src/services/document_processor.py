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
    Lança uma exceção em caso de falha para ser tratada no main.py.
    """
    if not api_key:
        raise ValueError("A chave de API não foi fornecida.")
    
    # A exceção real será gerada aqui se a chave for inválida ou a API não estiver ativa
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)


@st.cache_resource(show_spinner=False)
def obter_vector_store_de_uploads(lista_arquivos_pdf_upload, _embeddings_obj, api_key, _t):
    if not lista_arquivos_pdf_upload or not api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []
    llm_vision = None

    if api_key:
        try:
            llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=300)
        except Exception as e:
            st.warning(f"Não foi possível inicializar o modelo de visão do Gemini: {e}")
            llm_vision = None

    for arquivo_pdf_upload in lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_pdf_upload.name
        st.info(f"Processando arquivo: {nome_arquivo}...")
        documentos_arquivo_atual = []
        texto_extraido_com_sucesso = False
        temp_file_path = Path(f"temp_{nome_arquivo}")

        try:
            with open(temp_file_path, "wb") as f:
                f.write(arquivo_pdf_upload.getbuffer())

            # Tentativa 1: PyPDFLoader
            try:
                loader = PyPDFLoader(str(temp_file_path))
                pages_pypdf = loader.load()
                if pages_pypdf:
                    for page_num_pypdf, page_obj_pypdf in enumerate(pages_pypdf):
                        if page_obj_pypdf.page_content and page_obj_pypdf.page_content.strip():
                            doc = Document(page_content=page_obj_pypdf.page_content,
                                           metadata={"source": nome_arquivo, "page": page_obj_pypdf.metadata.get("page", page_num_pypdf), "method": "pypdf"})
                            documentos_arquivo_atual.append(doc)
                    
                    if any(doc.page_content.strip() for doc in documentos_arquivo_atual):
                        texto_extraido_com_sucesso = True
            except Exception:
                pass

            # Tentativa 2: PyMuPDF (fitz)
            if not texto_extraido_com_sucesso:
                try:
                    documentos_arquivo_atual = []
                    doc_fitz = fitz.open(str(temp_file_path))
                    for num_pagina, pagina_fitz in enumerate(doc_fitz):
                        texto_pagina = pagina_fitz.get_text("text")
                        if texto_pagina and texto_pagina.strip():
                            doc = Document(page_content=texto_pagina, metadata={"source": nome_arquivo, "page": num_pagina, "method": "pymupdf"})
                            documentos_arquivo_atual.append(doc)
                    doc_fitz.close()
                    if any(doc.page_content.strip() for doc in documentos_arquivo_atual):
                        texto_extraido_com_sucesso = True
                except Exception:
                    pass

            # Tentativa 3: Gemini Vision
            if not texto_extraido_com_sucesso and llm_vision:
                st.info(_t("info.extracting_text_with_gemini", filename=nome_arquivo))
                documentos_arquivo_atual = []
                try:
                    arquivo_pdf_upload.seek(0)
                    pdf_bytes = arquivo_pdf_upload.read()
                    doc_fitz_vision = fitz.open(stream=pdf_bytes, filetype="pdf")
                    
                    prompt_ocr = "Extraia todo o texto visível desta página."
                    
                    for page_num_gemini in range(len(doc_fitz_vision)):
                        page_fitz_obj = doc_fitz_vision.load_page(page_num_gemini)
                        pix = page_fitz_obj.get_pixmap(dpi=300) 
                        img_bytes = pix.tobytes("png")
                        base64_image = base64.b64encode(img_bytes).decode('utf-8')

                        human_message = HumanMessage(
                            content=[
                                {"type": "text", "text": prompt_ocr},
                                {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                            ]
                        )
                        
                        with st.spinner(_t("info.gemini_processing_page", page=page_num_gemini + 1, filename=nome_arquivo)):
                            ai_msg = llm_vision.invoke([human_message])
                        
                        if isinstance(ai_msg, AIMessage) and ai_msg.content and isinstance(ai_msg.content, str):
                            texto_pagina_gemini = ai_msg.content
                            if texto_pagina_gemini.strip():
                                doc = Document(page_content=texto_pagina_gemini, metadata={"source": nome_arquivo, "page": page_num_gemini, "method": "gemini_vision"})
                                documentos_arquivo_atual.append(doc)
                        time.sleep(2)

                    doc_fitz_vision.close()
                    if any(doc.page_content.strip() for doc in documentos_arquivo_atual):
                        texto_extraido_com_sucesso = True
                except Exception as e_gemini:
                    st.error(f"Erro ao usar Gemini Vision para {nome_arquivo}: {str(e_gemini)[:500]}")
            
            if texto_extraido_com_sucesso and documentos_arquivo_atual:
                documentos_totais.extend(documentos_arquivo_atual)
                nomes_arquivos_processados.append(nome_arquivo)
            else:
                st.error(f"Não foi possível extrair texto do arquivo: {nome_arquivo}.")

        except Exception as e_geral_arquivo:
            st.error(f"Erro geral ao processar o arquivo {nome_arquivo}: {e_geral_arquivo}")
        finally:
            if temp_file_path.exists():
                os.remove(temp_file_path)

    if not documentos_totais:
        return None, []

    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        docs_fragmentados = text_splitter.split_documents(documentos_totais)

        if not docs_fragmentados:
             return None, nomes_arquivos_processados

        vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
        return vector_store, nomes_arquivos_processados
    except Exception as e_faiss:
        st.error(f"Erro ao criar o vector store com FAISS: {e_faiss}")
        return None, nomes_arquivos_processados

