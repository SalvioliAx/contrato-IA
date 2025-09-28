import streamlit as st
import re
import traceback
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def processar_pergunta_chat(prompt, vector_store, t):
    """
    Processa a pergunta do utilizador, com logs detalhados para depuração.
    """
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    if 'chat_error' in st.session_state:
        del st.session_state['chat_error']

    try:
        if vector_store is None:
            raise ValueError("Vector store não foi inicializado corretamente.")

        # ATUALIZAÇÃO: Alterado o nome do modelo para uma versão estável
        llm_chat = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)
        
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
        
        partes_resposta = re.split(r'\|\|\|CLÁUSULA/ARTIGO PRINCIPAL:|\|\|\|TRECHO MAIS RELEVANTE DO CONTEXTO:', resposta_bruta)
        resposta_principal = partes_resposta[0].strip().replace("RESPOSTA (em Português):", "").strip()
        
        st.session_state.messages.append({
            "role": "assistant", "content": resposta_principal, "sources": fontes
        })

    except Exception:
        error_details = traceback.format_exc()
        st.session_state.chat_error = error_details
        st.session_state.messages.append({
            "role": "assistant",
            "content": t("errors.chat_processing_error")
        })

