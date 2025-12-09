 import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.chains.document.combine import StuffDocumentsChain
from langchain.chains import RetrievalQA

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": texts["chat_welcome_message"]}]

    # Exibe histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(texts["chat_expander_sources"]):
                    for doc in msg["sources"]:
                        metadata = doc.metadata
                        st.markdown(
                            f"**{texts['chat_source_label']}** `{metadata.get('source', 'N/A')}` "
                            f"({texts['chat_page_label']} {metadata.get('page', 'N/A')})"
                        )
                        st.markdown(f"> {doc.page_content.strip()}")
                        st.markdown("---")

    user_input = st.chat_input(texts["chat_input_placeholder"])
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        google_api_key=google_api_key
    )

    retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

    # Chat prompt moderno
    chat_prompt = ChatPromptTemplate([
        ("system", texts["chat_prompt"]),
        ("human", "{input}")
    ]).partial(language=lang_code)

    # StuffDocumentsChain moderno
    combine_chain = StuffDocumentsChain(llm=llm, prompt=chat_prompt)

    # RetrievalQA é a nova forma de criar a cadeia de Q&A com documentos
    chain = RetrievalQA(combine_documents_chain=combine_chain, retriever=retriever)

    # Execução da resposta
    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                result = chain.invoke({"query": user_input})

                answer = result.get("result")  # agora a chave padrão é "result"
                sources = result.get("source_documents", [])

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
