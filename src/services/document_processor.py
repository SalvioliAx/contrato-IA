import streamlit as st
import time
import base64
import fitz  # PyMuPDF

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.documents import Document

def get_embeddings_model(api_key: str):
    """Inicializa e retorna o modelo de embeddings da Google."""
    if not api_key:
        raise ValueError("A chave de API não foi fornecida.")
    try:
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    except Exception as e:
        raise ValueError(f"Falha ao inicializar o modelo de embeddings: {e}")

@st.cache_resource(show_spinner=False)
def obter_vector_store_de_uploads(_lista_arquivos_pdf_upload, _embeddings_obj, api_key, _t):
    """Processa ficheiros PDF carregados para criar um vector store FAISS."""
    if not _lista_arquivos_pdf_upload or not api_key or not _embeddings_obj:
        return None, None

    documentos_totais = []
    nomes_arquivos_processados = []
    
    llm_vision = None # Inicializado apenas se for necessário
    if api_key:
        try:
            # CORREÇÃO: Padronizado para um nome de modelo válido e estável.
            llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=300)
        except Exception as e:
            st.warning(_t("warnings.vision_model_init_failed", error=e))

    for arquivo_pdf in _lista_arquivos_pdf_upload:
        nome_arquivo = arquivo_pdf.name
        texto_extraido = False
        documentos_do_arquivo = []

        try:
            arquivo_pdf.seek(0)
            pdf_bytes = arquivo_pdf.read()
            
            # Tentativa 1: PyMuPDF (fitz)
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz:
                for num_pagina, pagina in enumerate(doc_fitz):
                    texto_pagina = pagina.get_text("text")
                    if texto_pagina and texto_pagina.strip():
                        documentos_do_arquivo.append(Document(page_content=texto_pagina, metadata={"source": nome_arquivo, "page": num_pagina}))
                        texto_extraido = True
            
            # Tentativa 2: Gemini Vision (se PyMuPDF falhar)
            if not texto_extraido and llm_vision:
                st.sidebar.warning(_t("warnings.pymupdf_failed_trying_gemini", filename=nome_arquivo))
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_vision:
                    for page_num in range(len(doc_fitz_vision)):
                        page_obj = doc_fitz_vision.load_page(page_num)
                        pix = page_obj.get_pixmap(dpi=300)
                        img_bytes = pix.tobytes("png")
                        base64_image = base64.b64encode(img_bytes).decode('utf-8')
                        
                        human_message = HumanMessage(content=[
                            {"type": "text", "text": _t("analysis.ocr_prompt")},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                        ])
                        
                        ai_msg = llm_vision.invoke([human_message])
                        texto_pagina_gemini = ai_msg.content if isinstance(ai_msg, AIMessage) else ""

                        if texto_pagina_gemini and texto_pagina_gemini.strip():
                            documentos_do_arquivo.append(Document(page_content=texto_pagina_gemini, metadata={"source": nome_arquivo, "page": page_num}))
                            texto_extraido = True
                        time.sleep(2)

            if texto_extraido:
                documentos_totais.extend(documentos_do_arquivo)
                nomes_arquivos_processados.append(nome_arquivo)
            else:
                st.sidebar.error(_t("errors.text_extraction_failed", filename=nome_arquivo))

        except Exception as e:
            st.sidebar.error(_t("errors.file_processing_error", filename=nome_arquivo, error=e))

    if not documentos_totais:
        return None, []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    docs_fragmentados = text_splitter.split_documents(documentos_totais)
    
    vector_store = FAISS.from_documents(docs_fragmentados, _embeddings_obj)
    return vector_store, nomes_arquivos_processados
