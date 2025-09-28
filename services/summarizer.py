import streamlit as st
import fitz
import base64, time, os
from pathlib import Path
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

@st.cache_data(show_spinner="Gerando resumo...")
def gerar_resumo_executivo(arquivo_pdf_bytes, nome_arquivo_original, google_api_key):
    if not arquivo_pdf_bytes or not google_api_key:
        return "Erro: sem arquivo ou chave API."

    texto = ""
    try:
        with fitz.open(stream=arquivo_pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                texto += page.get_text() + "\n"
    except Exception:
        return "Erro ao extrair texto do PDF."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    prompt = PromptTemplate.from_template(
        "Resuma o contrato abaixo em 5 a 7 tópicos:\n{texto_contrato}\n\nResumo:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({"texto_contrato": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro no resumo: {e}"
