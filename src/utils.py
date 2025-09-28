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
    """Extrai o texto completo de uma lista de ficheiros carregados."""
    textos_completos = []
    for file in uploaded_files:
        try:
            file.seek(0)
            pdf_bytes = file.read()
            texto_doc = ""
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz:
                texto_doc = "".join(page.get_text() for page in doc_fitz)
            
            if not texto_doc.strip():
                st.info(t("info.extracting_text_with_gemini", filename=file.name))
                # ATUALIZAÇÃO: Alterado o nome do modelo para uma versão estável
                llm_vision = ChatGoogleGenerativeAI(model="gemini-pro-vision", temperature=0.1)
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_vision:
                    for page_num in range(len(doc_fitz_vision)):
                        # ... (lógica de extração com Gemini Vision) ...
                        pass
            
            textos_completos.append({"nome": file.name, "texto": texto_doc})
        except Exception as e:
            st.error(f"Erro ao ler {file.name}: {e}")
    return textos_completos

def formatar_chat_para_markdown(mensagens, t):
    """Formata o histórico do chat para exportação em Markdown."""
    texto_formatado = f"# {t('chat.export_title')}\n\n"
    for msg in mensagens:
        if msg["role"] == "user":
            texto_formatado += f"## {t('chat.export_user_title')}:\n{msg['content']}\n\n"
        elif msg["role"] == "assistant":
            texto_formatado += f"## {t('chat.export_ia_title')}:\n{msg['content']}\n\n"
    return texto_formatado

