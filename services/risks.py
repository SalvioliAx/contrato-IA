import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Analisando documento para riscos contratuais...")
def analisar_documento_para_riscos(texto, nome_arquivo, google_api_key):
    """
    Analisa o texto de um contrato e gera um relatório sobre riscos potenciais.
    """
    if not texto or not google_api_key:
        return "Erro: Texto do documento ou chave da API não fornecidos."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
    prompt = PromptTemplate.from_template(
        "Você é um advogado especialista em riscos. Analise o contrato '{nome}' e identifique cláusulas ou omissões que representem riscos (financeiros, legais, operacionais, etc.). "
        "Para cada risco, descreva-o, cite o trecho relevante e classifique-o.\n\n"
        "Texto do Contrato:\n{texto}\n\n"
        "RELATÓRIO DE RISCOS:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        # Limita o tamanho do texto enviado
        res = chain.invoke({"nome": nome_arquivo, "texto": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro ao gerar análise de riscos: {e}"
