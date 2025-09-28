import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.locale import TRANSLATIONS

@st.cache_data # Removido show_spinner
def verificar_conformidade_documento(ref_texto, ref_nome, doc_texto, doc_nome, google_api_key, lang_code):
    """
    Verifica a conformidade entre dois documentos, com prompt sensível ao idioma.
    """
    if not ref_texto or not doc_texto or not google_api_key:
        return "Erro: faltam dados ou chave API."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    
    language_name = TRANSLATIONS[lang_code]["lang_selector_label"]
    prompt_template = (
        "Você é um especialista em conformidade. Compare o DOCUMENTO A ANALISAR ({doc_nome}) "
        "com o DOCUMENTO DE REFERÊNCIA ({ref_nome}). "
        "Seu relatório final deve ser escrito em {language}.\n\n"
        "Documento de referência:\n{ref}\n\nDocumento a analisar:\n{doc}\n\nRelatório de conformidade:"
    )
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        res = chain.invoke({
            "doc_nome": doc_nome,
            "ref_nome": ref_nome,
            "language": language_name,
            "ref": ref_texto[:25000],
            "doc": doc_texto[:25000]
        })
        return res['text']
    except Exception as e:
        return f"Erro na análise de conformidade: {e}"

