import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.locale import TRANSLATIONS

@st.cache_data(show_spinner="Analyzing document for contractual risks...")
def analisar_documento_para_riscos(texto, nome_arquivo, google_api_key, lang_code):
    if not texto or not google_api_key:
        return "Error: Document text or API key not provided."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
    prompt_template_str = TRANSLATIONS[lang_code]['risks_prompt']
    prompt = PromptTemplate.from_template(prompt_template_str)
    
    chain = LLMChain(llm=llm, prompt=prompt.partial(language=lang_code))

    try:
        res = chain.invoke({"nome": nome_arquivo, "texto": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Error generating risk analysis: {e}"

