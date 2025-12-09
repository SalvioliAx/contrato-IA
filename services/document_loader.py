import streamlit as st
import os, time, base64
from pathlib import Path
import fitz

# --- CORREÇÕES DE IMPORTAÇÃO (LangChain Novo) ---
# PyPDFLoader agora mora na community
from langchain_community.document_loaders import PyPDFLoader
# FAISS agora mora na community
from langchain_community.vectorstores import FAISS
# RecursiveCharacterTextSplitter deve vir daqui se o pacote 'langchain-text-splitters' não estiver explícito
from langchain.text_splitter import RecursiveCharacterTextSplitter
# ------------------------------------------------

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage

@st.cache_resource
def obter_vector_store_de_uploads(lista_arquivos_pdf_upload, _embeddings_obj, google_api_key):
    if not lista_arquivos_pdf_upload or not google_api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []

    try:
        # MANTIDO O MODELO 2.5-PRO CONFORME SUA SOLICITAÇÃO
        llm_vision = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            temperature=0.1, 
            request_timeout=300,
            google_api_key=google_api_key
        )
    except Exception as e:
        st.warning(f"Não foi possível inicializar o modelo de visão do Gemini: {e}")
        llm_vision = None

    for arquivo_pdf_upload in lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_pdf_upload.name
        documentos_arquivo_atual = []
        texto_extraido_com_sucesso = False
        temp_file_path = Path(f"temp_{nome_arquivo}")

        try:
            with open(temp_file_path, "wb") as f:
                f.write(arquivo_pdf_upload.getbuffer())

            # Tentativa 1: PyPDFLoader
            try:
                loader = PyPDFLoader(str(temp_file_path))
                pages = loader.load()
                for page_num, page_obj in enumerate(pages):
                    if page_obj.page_content.strip():
                        doc = Document(
                            page_content=page_obj.page_content,
                            metadata={"source": nome_arquivo, "page": page_num, "method": "pypdf"}
                        )
                        documentos_arquivo_atual.append(doc)
                if documentos_arquivo_atual:
                    texto_extraido_com_sucesso = True
            except Exception:
                pass 

            # Tentativa 2: PyMuPDF
            if not texto_extraido_com_sucesso:
                try:
                    documentos_arquivo_atual = []
                    doc_fitz = fitz.open(str(temp_file_path))
                    for num_pagina, pagina in enumerate(doc_fitz):
                        texto = pagina.get_text("text")
                        if texto.strip():
                            doc = Document(
                                page_content=texto,
                                metadata={"source": nome_arquivo, "page": num_pagina, "method": "pymupdf"}
                            )
                            documentos_arquivo_atual.append(doc)
                    doc_fitz.close()
                    if documentos_arquivo_atual:
                        texto_extraido_com_sucesso = True
                except Exception:
                    pass

            # Tentativa 3: Gemini Vision OCR
            if not texto_extraido_com_sucesso and llm_vision:
                documentos_arquivo_atual = []
                try:
                    arquivo_pdf_upload.seek(0)
                    pdf_bytes = arquivo_pdf_upload.read()
                    doc_fitz_vision = fitz.open(stream=pdf_bytes, filetype="pdf")

                    prompt = "Você é um especialista em OCR. Extraia todo o texto desta página."

                    for page_num in range(len(doc_fitz_vision)):
                        page = doc_fitz_vision.load_page(page_num)
                        pix = page.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes("png")
                        base64_image = base64.b64encode(img_bytes).decode("utf-8")

                        human_message = HumanMessage(content=[
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                        ])

                        ai_msg = llm_vision.invoke([human_message])

                        if isinstance(ai_msg, AIMessage) and isinstance(ai_msg.content, str):
                            doc = Document(
                                page_content=ai_msg.content,
                                metadata={"source": nome_arquivo, "page": page_num, "method": "gemini_vision"}
                            )
                            documentos_arquivo_atual.append(doc)
                        time.sleep(2)

                    doc_fitz_vision.close()
                    if documentos_arquivo_atual:
                        texto_extraido_com_sucesso = True
                except Exception:
                     pass

            if texto_extraido_com_sucesso:
                documentos_totais.extend(documentos_arquivo_atual)
                nomes_arquivos_processados.append(nome_arquivo)
            else:
                st.error(f"Não foi possível extrair texto de {nome_arquivo}.")

        finally:
            if temp_file_path.exists():
                try: os.remove(temp_file_path)
                except: pass

    if not documentos_totais:
        return None, []

    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    docs_fragmentados = splitter.split_documents(documentos_totais)
    
    vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
    return vector_store, nomes_arquivos_processados
