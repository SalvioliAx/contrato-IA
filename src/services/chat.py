import streamlit as st
import re
import traceback
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def processar_pergunta_chat(prompt: str, vector_store, t):
    """
    Processa a pergunta do utilizador, extrai a resposta e as fontes,
    e armazena no estado da sessão para exibição.
    """
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    if 'chat_error' in st.session_state:
        del st.session_state['chat_error']

    try:
        if vector_store is None:
            raise ValueError(t("errors.vector_store_not_initialized"))

        # CORREÇÃO: Padronizado para um nome de modelo válido e estável.
        llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
        
        template = t("chat.prompt_template")
        prompt_template = PromptTemplate.from_template(template)

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_chat,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 7}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )

        resultado = qa_chain.invoke({"query": prompt})
        resposta_bruta = resultado.get("result", "")
        fontes = resultado.get("source_documents", [])

        # --- LÓGICA DE PARSING CORRIGIDA PARA RESTAURAR CITAÇÕES ---
        resposta_principal = resposta_bruta
        clausula_citada = None
        sentenca_chave = None

        if '|||CLÁUSULA/ARTIGO PRINCIPAL:' in resposta_bruta:
            partes = resposta_bruta.split('|||CLÁUSULA/ARTIGO PRINCIPAL:', 1)
            resposta_principal = partes[0]
            resto = partes[1] if len(partes) > 1 else ""
            
            if '|||TRECHO MAIS RELEVANTE DO CONTEXTO:' in resto:
                sub_partes = resto.split('|||TRECHO MAIS RELEVANTE DO CONTEXTO:', 1)
                clausula_citada = sub_partes[0].strip()
                sentenca_chave = sub_partes[1].strip() if len(sub_partes) > 1 else None
            else:
                clausula_citada = resto.strip()

        elif '|||TRECHO MAIS RELEVANTE DO CONTEXTO:' in resposta_bruta:
            partes = resposta_bruta.split('|||TRECHO MAIS RELEVANTE DO CONTEXTO:', 1)
            resposta_principal = partes[0]
            sentenca_chave = partes[1].strip() if len(partes) > 1 else None

        resposta_principal = re.sub(r"RESPOSTA \((em|in|en) .*\):", "", resposta_principal, flags=re.IGNORECASE).strip()
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": resposta_principal, 
            "sources": fontes,
            "clausula_citada": clausula_citada,
            "sentenca_chave": sentenca_chave
        })

    except Exception:
        error_details = traceback.format_exc()
        st.session_state.chat_error = error_details
        st.session_state.messages.append({
            "role": "assistant",
            "content": t("errors.chat_processing_error")
        })
