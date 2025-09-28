import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Checking document compliance...")
def verificar_conformidade_documento(ref_texto, ref_nome, doc_texto, doc_nome, google_api_key, lang_code):
    if not ref_texto or not doc_texto or not google_api_key:
        return "Error: Document texts or API key missing."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    prompt = PromptTemplate.from_template(
        "You are an auditor. Compare 'DOCUMENT TO ANALYZE' ({doc_nome}) with 'REFERENCE DOCUMENT' ({ref_nome}).\n"
        "Identify and list clauses in 'DOCUMENT TO ANALYZE' that contradict or are misaligned with 'REFERENCE DOCUMENT'.\n"
        "Your response must be in {language}.\n\n"
        "Reference Document:\n{ref}\n\n"
        "Document to Analyze:\n{doc}\n\n"
        "COMPLIANCE REPORT:"
    )
    chain = LLMChain(llm=llm, prompt=prompt.partial(language=lang_code))
    try:
        res = chain.invoke({
            "ref_nome": ref_nome, "ref": ref_texto[:25000],
            "doc_nome": doc_nome, "doc": doc_texto[:25000]
        })
        return res['text']
    except Exception as e:
        return f"Error in compliance analysis: {e}"

