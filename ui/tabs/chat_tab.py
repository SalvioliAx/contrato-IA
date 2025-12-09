import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Renderiza a aba de Chat, agora usando textos localizados e prompt sensível ao idioma.
    """
    st.header(texts["chat_header"])

    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": texts["chat_welcome_message"]}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(texts["chat_expander_sources"]):
                    for doc in msg["sources"]:
                        metadata = doc.metadata
                        st.markdown(f"**{texts['chat_source_label']}** `{metadata.get('source', 'N/A')}` ({texts['chat_page_label']} {metadata.get('page', 'N/A')})")
                        st.markdown(f"> {doc.page_content.strip()}")
                        st.markdown("---")

    user_input = st.chat_input(texts["chat_input_placeholder"])
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
        retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

        prompt_template_str = texts["chat_prompt"]
        prompt = PromptTemplate.from_template(prompt_template_str)

        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt.partial(language=lang_code)}
        )

        with st.chat_message("assistant"):
            with st.spinner(texts["chat_spinner_thinking"]):
                try:
                    result = chain.invoke({"query": user_input})
                    st.session_state.messages.append({"role": "assistant", "content": result["result"], "sources": result["source_documents"]})
                    st.rerun()
                except Exception as e:
                    st.error(f"{texts['chat_error']} {e}")




