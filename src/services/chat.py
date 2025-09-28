import streamlit as st
import re
import traceback  # Módulo para obter o erro detalhado
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
    # Limpa erros anteriores ao processar uma nova pergunta
    if 'chat_error' in st.session_state:
        del st.session_state['chat_error']

    try:
        print("--- DEBUG: Iniciando processamento do chat ---")
        if vector_store is None:
            print("--- DEBUG: ERRO: Vector store é Nulo. Abortando. ---")
            raise ValueError("Vector store não foi inicializado corretamente.")

        print(f"--- DEBUG: Prompt do utilizador: {prompt} ---")
        print("--- DEBUG: Inicializando o LLM (gemini-1.5-flash-latest)... ---")
        llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
        print("--- DEBUG: LLM inicializado com sucesso. ---")

        template = t("chat.prompt_template")
        prompt_template = PromptTemplate.from_template(template)
        print("--- DEBUG: Template de prompt criado. ---")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_chat,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 7}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )
        print("--- DEBUG: Cadeia RetrievalQA criada. Invocando a cadeia... ---")

        resultado = qa_chain.invoke({"query": prompt})
        print("--- DEBUG: Cadeia invocada com sucesso. ---")

        resposta_bruta = resultado.get("result", "")
        fontes = resultado.get("source_documents", [])
        
        print("--- DEBUG: Iniciando parsing da resposta... ---")
        resposta_principal = resposta_bruta
        # ... (lógica de parsing da resposta) ...
        print("--- DEBUG: Parsing concluído. ---")
        
        st.session_state.messages.append({
            "role": "assistant", "content": resposta_principal, "sources": fontes
        })
        print("--- DEBUG: Processamento do chat concluído com sucesso. ---")

    except Exception:
        print("--- DEBUG: !!! ERRO CAPTURADO no bloco except !!! ---")
        # Captura o traceback completo como uma string
        error_details = traceback.format_exc()
        print(error_details)  # Isto aparecerá nos logs do Streamlit Cloud

        # Guarda o erro detalhado no estado da sessão para ser exibido na UI
        st.session_state.chat_error = error_details

        st.session_state.messages.append({
            "role": "assistant",
            "content": t("errors.chat_processing_error")
        })

