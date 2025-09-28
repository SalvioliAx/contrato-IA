import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.locale import TRANSLATIONS

@st.cache_data # Removido show_spinner
def analisar_documento_para_riscos(texto, nome_arquivo, google_api_key, lang_code):
    """
    Analisa um documento para riscos, agora com prompt sensível ao idioma.
    """
    if not texto or not google_api_key:
        return "Erro: sem texto ou API."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
    
    prompt_text = TRANSLATIONS[lang_code]["risks_prompt"].format(nome=nome_arquivo, language=TRANSLATIONS[lang_code]["lang_selector_label"])
    
    prompt = PromptTemplate.from_template(
        prompt_text + "\n\nTEXTO DO CONTRATO:\n{texto}\n\nANÁLISE DE RISCOS:"
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({"texto": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro na análise de riscos: {e}"


