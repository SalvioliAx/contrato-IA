import streamlit as st
import fitz
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.locale import TRANSLATIONS

@st.cache_data # Removido show_spinner
def gerar_resumo_executivo(arquivo_pdf_bytes, nome_arquivo_original, google_api_key, lang_code):
    """
    Gera um resumo executivo de um documento PDF, agora sensível ao idioma.
    """
    if not arquivo_pdf_bytes or not google_api_key:
        return "Erro: sem arquivo ou chave API."

    texto = ""
    try:
        with fitz.open(stream=arquivo_pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                texto += page.get_text() + "\n"
    except Exception:
        return "Erro ao extrair texto do PDF."

    if not texto.strip():
        return "Não foi possível extrair conteúdo de texto do documento."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    
    prompt_text = TRANSLATIONS[lang_code]["summary_prompt"].format(language=TRANSLATIONS[lang_code]["lang_selector_label"])
    
    prompt = PromptTemplate.from_template(
        prompt_text + "\n\nCONTRATO:\n{texto_contrato}\n\nRESUMO:"
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({"texto_contrato": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro no resumo: {e}"

