import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.combine_documents.base import StuffDocumentsChain
from langchain.chains import create_retrieval_chain

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": texts["chat_welcome_message"]}
        ]

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

    # LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        google_api_key=google_api_key
    )

    retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

    # Prompt simples compatível
    prompt_template = texts.get("chat_prompt", "{input}")
    prompt = PromptTemplate.from_template(prompt_template)
    prompt = prompt.partial(language=lang_code)

    combine_chain = StuffDocumentsChain(llm=llm, prompt=prompt)
    chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=combine_chain
    )

    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                result = chain.invoke({"input": user_input})
                answer = result["answer"]
                sources = result.get("context", [])

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
