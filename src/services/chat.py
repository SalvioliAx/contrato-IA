import re
import streamlit as st
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def processar_pergunta_chat(prompt: str, vector_store, idioma: str, t) -> dict:
    """
    Processa uma pergunta do utilizador, realiza uma busca na base de vetores
    e retorna a resposta formatada da IA.
    """
    if not vector_store:
        return {
            "role": "assistant",
            "content": t("errors.vector_store_not_ready")
        }

    llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
    
    # Usa o tradutor 't' para obter o template do prompt no idioma correto
    template_prompt_chat = PromptTemplate.from_template(t(f"prompts.chat_template_{idioma}"))

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_chat,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 7}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": template_prompt_chat}
    )

    resultado = qa_chain.invoke({"query": prompt})
    resposta_bruta = resultado["result"]
    fontes = resultado["source_documents"]

    # Extrai as partes da resposta com base nos separadores definidos no prompt
    resposta_principal = resposta_bruta
    clausula_citada = None
    sentenca_chave = None

    separador_clausula = '|||CLÁUSULA/ARTIGO PRINCIPAL:'
    separador_trecho = '|||TRECHO MAIS RELEVANTE DO CONTEXTO:'

    if separador_clausula in resposta_bruta:
        partes = resposta_bruta.split(separador_clausula, 1)
        resposta_principal = partes[0].strip()
        resto = partes[1]
        
        if separador_trecho in resto:
            partes_resto = resto.split(separador_trecho, 1)
            clausula_citada = partes_resto[0].strip()
            sentenca_chave = partes_resto[1].strip()
        else:
            clausula_citada = resto.strip()
    
    elif separador_trecho in resposta_bruta:
        partes = resposta_bruta.split(separador_trecho, 1)
        resposta_principal = partes[0].strip()
        sentenca_chave = partes[1].strip()

    # Limpeza final da resposta
    resposta_principal = re.sub(r"RESPOSTA \(.*\):", "", resposta_principal).strip()
    if not clausula_citada or t("prompts.not_applicable") in clausula_citada.lower():
        clausula_citada = None

    return {
        "role": "assistant",
        "content": resposta_principal,
        "sources": fontes,
        "sentenca_chave": sentenca_chave,
        "clausula_citada": clausula_citada
    }

