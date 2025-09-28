import streamlit as st
from datetime import datetime
import fitz  # PyMuPDF
import time
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

def reset_analysis_data():
    """Limpa os dados de análise da sessão para forçar um recálculo."""
    keys_to_clear = [
        'df_dashboard', 'resumo_gerado', 'arquivo_resumido',
        'analise_riscos_resultados', 'eventos_contratuais_df',
        'conformidade_resultados', 'anomalias_resultados'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def formatar_chat_para_markdown(mensagens_chat, t):
    """Formata o histórico do chat para exportação em Markdown."""
    texto_formatado = f"# {t('chat.export_title')}\n\n"
    for mensagem in mensagens_chat:
        if mensagem["role"] == "user":
            texto_formatado += f"## {t('chat.export_user_label')}:\n{mensagem['content']}\n\n"
        elif mensagem["role"] == "assistant":
            texto_formatado += f"## {t('chat.export_ia_label')}:\n{mensagem['content']}\n"
            if "sources" in mensagem and mensagem["sources"]:
                texto_formatado += f"### {t('chat.export_sources_label')}:\n"
                for i, doc_fonte in enumerate(mensagem["sources"]):
                    source_name = doc_fonte.metadata.get('source', 'N/A')
                    page_num = doc_fonte.metadata.get('page', 'N/A')
                    texto_formatado += f"- **{t('chat.export_source_item_label', num=i+1, doc=source_name, page=page_num)}**:\n  > {doc_fonte.page_content[:500]}...\n\n"
            texto_formatado += "---\n\n"
    return texto_formatado

def get_full_text_from_uploads(lista_arquivos_upload, t):
    """
    Extrai o texto completo de uma lista de ficheiros PDF carregados.
    Usa PyMuPDF e tem um fallback para Gemini Vision se necessário.
    """
    if not lista_arquivos_upload:
        return []

    textos_completos = []
    for arquivo_obj in lista_arquivos_upload:
        texto_doc = ""
        try:
            arquivo_obj.seek(0)  # Resetar ponteiro do ficheiro
            pdf_bytes = arquivo_obj.read()
            
            # Tentativa 1: PyMuPDF
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz:
                for page in doc_fitz:
                    texto_doc += page.get_text() + "\n"
            
            # Tentativa 2: Fallback para Gemini Vision se o texto for insuficiente
            if not texto_doc.strip() or len(texto_doc.strip()) < 100:
                st.info(t("info.pymupdf_failed_trying_gemini", name=arquivo_obj.name))
                texto_gemini = ""
                llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
                
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_gemini:
                    prompt_ocr = "Extraia todo o texto desta página de documento da forma mais precisa possível."
                    num_paginas_a_processar = min(len(doc_fitz_gemini), 10)

                    for page_num in range(num_paginas_a_processar):
                        page_obj_gemini = doc_fitz_gemini.load_page(page_num)
                        pix = page_obj_gemini.get_pixmap(dpi=200)
                        img_bytes_ocr = pix.tobytes("png")
                        base64_image_ocr = base64.b64encode(img_bytes_ocr).decode('utf-8')
                        
                        msg = HumanMessage(content=[
                            {"type": "text", "text": prompt_ocr},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image_ocr}"}
                        ])

                        with st.spinner(t("info.gemini_processing_page", page=page_num + 1, total=num_paginas_a_processar, name=arquivo_obj.name)):
                            ai_msg = llm_vision.invoke([msg])
                        
                        if isinstance(ai_msg, AIMessage) and ai_msg.content and isinstance(ai_msg.content, str):
                            texto_gemini += ai_msg.content + "\n\n"
                        time.sleep(1.5)
                
                if texto_gemini.strip():
                    texto_doc = texto_gemini
                else:
                    st.warning(t("warnings.text_extraction_failed_both_methods", name=arquivo_obj.name))

            if texto_doc.strip():
                textos_completos.append({"nome": arquivo_obj.name, "texto": texto_doc})

        except Exception as e:
            st.error(t("errors.error_reading_file_for_analysis", name=arquivo_obj.name, error=str(e)))
            
    return textos_completos

