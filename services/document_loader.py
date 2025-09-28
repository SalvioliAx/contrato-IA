import streamlit as st
import os, time, base64
from pathlib import Path
import fitz  # PyMuPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

@st.cache_resource(show_spinner="Analisando documentos...")
def obter_vector_store_de_uploads(lista_arquivos_pdf_upload, _embeddings_obj, google_api_key):
    if not lista_arquivos_pdf_upload or not google_api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []

    # Modelo Gemini para OCR fallback
    try:
        llm_vision = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", temperature=0.1, request_timeout=300
        )
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
                    st.success(f"Texto extraído com PyPDFLoader para {nome_arquivo}.")
            except Exception as e_pypdf:
                st.warning(f"PyPDFLoader falhou: {e_pypdf}. Tentando PyMuPDF...")

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
                        st.success(f"Texto extraído com PyMuPDF para {nome_arquivo}.")
                except Exception as e_fitz:
                    st.warning(f"PyMuPDF falhou: {e_fitz}")

            # Tentativa 3: Gemini Vision OCR
            if not texto_extraido_com_sucesso and llm_vision:
                st.info(f"Tentando Gemini Vision OCR para {nome_arquivo}...")
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

                        with st.spinner(f"Gemini processando página {page_num+1}..."):
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
                        st.success(f"Texto extraído com Gemini Vision para {nome_arquivo}.")
                except Exception as e_gemini:
                    st.error(f"Erro no Gemini Vision OCR: {e_gemini}")

            # Finalização
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
        st.error("Nenhum texto pôde ser extraído dos documentos.")
        return None, []

    # Fragmentação e criação do FAISS
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        docs_fragmentados = splitter.split_documents(documentos_totais)
        st.info(f"Criando vector store com {len(docs_fragmentados)} fragmentos.")
        vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
        return vector_store, nomes_arquivos_processados
    except Exception as e_faiss:
        st.error(f"Erro ao criar vector store: {e_faiss}")
        return None, nomes_arquivos_processados
