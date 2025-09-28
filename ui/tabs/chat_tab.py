import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain

def render_chat_tab(embeddings_global, google_api_key):
    st.header("💬 Chat com Contratos")

    if "vector_store_atual" not in st.session_state:
        st.info("Carregue documentos primeiro.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Digite sua pergunta sobre os contratos...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
        retriever = st.session_state.vector_store_atual.as_retriever()
        chain = ConversationalRetrievalChain.from_llm(llm, retriever)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                result = chain.invoke({"question": user_input, "chat_history": []})
                resposta = result["answer"]
                st.markdown(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
