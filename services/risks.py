import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Analisando riscos...")
def analisar_documento_para_riscos(texto, nome_arquivo, google_api_key):
    if not texto or not google_api_key:
        return "Erro: sem texto ou API."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
    prompt = PromptTemplate.from_template(
        "Analise o contrato ({nome}) e identifique riscos contratuais:\n{texto}\n\nRelatório:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({"nome": nome_arquivo, "texto": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro na análise de riscos: {e}"
