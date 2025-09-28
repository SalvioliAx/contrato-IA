import streamlit as st
import fitz  # PyMuPDF
import base64
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

def reset_analysis_data():
    """Limpa todos os dados de análise em cache no estado da sessão."""
    keys_to_clear = [
        'df_dashboard', 'resumo_gerado', 'arquivo_resumido', 
        'analise_riscos_resultados', 'eventos_contratuais_df', 
        'conformidade_resultados', 'anomalias_resultados'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_full_text_from_uploads(uploaded_files, t):
    """Extrai o texto completo de uma lista de ficheiros carregados, com fallback para IA."""
    textos_completos = []
    if not uploaded_files:
        return textos_completos

    for file in uploaded_files:
        texto_doc = ""
        try:
            file.seek(0)
            pdf_bytes = file.read()
            
            # Tenta extrair com PyMuPDF
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz:
                for page in doc_fitz:
                    texto_doc += page.get_text() + "\n"
            
            # Se PyMuPDF não extrair texto, tenta com Gemini Vision
            if not texto_doc.strip():
                st.info(t("info.extracting_text_with_gemini", filename=file.name))
                # CORREÇÃO FINAL: Usando o nome do modelo especificado pelo utilizador.
                llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
                
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_vision:
                    for page_num in range(len(doc_fitz_vision)):
                        page_obj = doc_fitz_vision.load_page(page_num)
                        pix = page_obj.get_pixmap(dpi=200)
                        img_bytes_ocr = pix.tobytes("png")
                        base64_image_ocr = base64.b64encode(img_bytes_ocr).decode('utf-8')
                        
                        human_message_ocr = HumanMessage(content=[
                            {"type": "text", "text": t("analysis.ocr_prompt")},
                            {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image_ocr}"}
                        ])
                        
                        ai_msg_ocr = llm_vision.invoke([human_message_ocr])
                        if isinstance(ai_msg_ocr, AIMessage) and ai_msg_ocr.content:
                            texto_doc += ai_msg_ocr.content + "\n\n"
                        time.sleep(1)

            if texto_doc.strip():
                textos_completos.append({"nome": file.name, "texto": texto_doc})
            else:
                st.warning(t("warnings.text_extraction_failed_for_file", filename=file.name))

        except Exception as e:
            st.error(t("errors.file_processing_error", filename=file.name, error=e))
            
    return textos_completos

def formatar_chat_para_markdown(mensagens, t):
    """Formata o histórico do chat para exportação em Markdown."""
    texto_formatado = f"# {t('chat.export_title')}\n\n"
    for msg in mensagens:
        if msg["role"] == "user":
            texto_formatado += f"## {t('chat.export_user_title')}:\n{msg['content']}\n\n"
        elif msg["role"] == "assistant":
            texto_formatado += f"## {t('chat.export_ai_title')}:\n{msg['content']}\n"
            if "sources" in msg and msg["sources"]:
                texto_formatado += f"### {t('chat.export_sources_title')}:\n"
                for i, doc in enumerate(msg["sources"]):
                    source_name = doc.metadata.get('source', 'N/A')
                    page_num = doc.metadata.get('page', 'N/A')
                    texto_formatado += f"- **{t('chat.export_source_item', index=i+1, source=source_name, page=page_num)}**:\n  > {doc.page_content[:500]}...\n\n"
            texto_formatado += "---\n\n"
    return texto_formatado

