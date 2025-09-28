import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Verificando conformidade entre documentos...")
def verificar_conformidade_documento(ref_texto, ref_nome, doc_texto, doc_nome, google_api_key):
    """
    Compara um documento com um documento de referência para encontrar não conformidades.
    """
    if not ref_texto or not doc_texto or not google_api_key:
        return "Erro: Faltam textos dos documentos ou a chave da API."

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
    prompt = PromptTemplate.from_template(
        "Você é um auditor. Compare o 'DOCUMENTO A ANALISAR' ({doc_nome}) com o 'DOCUMENTO DE REFERÊNCIA' ({ref_nome}).\n"
        "Identifique e liste cláusulas no 'DOCUMENTO A ANALISAR' que contradigam ou estejam em desalinhamento com o 'DOCUMENTO DE REFERÊNCIA'.\n\n"
        "Documento de Referência:\n{ref}\n\n"
        "Documento a Analisar:\n{doc}\n\n"
        "RELATÓRIO DE CONFORMIDADE:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        # Limita o tamanho do contexto para evitar exceder o limite de tokens
        res = chain.invoke({
            "ref_nome": ref_nome, "ref": ref_texto[:25000],
            "doc_nome": doc_nome, "doc": doc_texto[:25000]
        })
        return res['text']
    except Exception as e:
        return f"Erro na análise de conformidade: {e}"
