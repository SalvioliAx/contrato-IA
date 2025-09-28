import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Verificando conformidade...")
def verificar_conformidade_documento(ref_texto, ref_nome, doc_texto, doc_nome, google_api_key):
    if not ref_texto or not doc_texto or not google_api_key:
        return "Erro: faltam dados ou chave API."

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
    prompt = PromptTemplate.from_template(
        "Compare o DOCUMENTO A ANALISAR ({doc_nome}) com o DOCUMENTO DE REFERÊNCIA ({ref_nome}).\n\n"
        "Documento de referência:\n{ref}\n\nDocumento a analisar:\n{doc}\n\nRelatório de conformidade:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({
            "ref_nome": ref_nome, "ref": ref_texto[:25000],
            "doc_nome": doc_nome, "doc": doc_texto[:25000]
        })
        return res['text']
    except Exception as e:
        return f"Erro na análise de conformidade: {e}"
