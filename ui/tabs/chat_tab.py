import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
# Estas são as substitutas oficiais do RetrievalQA:
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    # 1. Verifica se documentos foram processados
    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    # 2. Inicializa histórico
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": texts["chat_welcome_message"]}
        ]

    # 3. Exibe histórico visual
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(texts["chat_expander_sources"]):
                    for doc in msg["sources"]:
                        metadata = doc.metadata
                        st.markdown(f"**{texts['chat_source_label']}** `{metadata.get('source', 'N/A')}`")
                        st.caption(f"{doc.page_content[:300]}...")
                        st.markdown("---")

    # 4. Input do usuário
    user_input = st.chat_input(texts["chat_input_placeholder"])
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- LÓGICA RAG MODERNA (Substituindo RetrievalQA) ---
    
    # 1. Modelo (Mantido 2.5-pro)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        google_api_key=google_api_key
    )

    # 2. Retriever
    retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

    # 3. Prompt (Adaptação Inteligente)
    # A nova chain exige que a pergunta se chame '{input}' e o contexto '{context}'
    raw_prompt = texts.get("chat_prompt", "")
    
    # Se o seu texto usa '{question}', trocamos por '{input}' para não quebrar
    raw_prompt = raw_prompt.replace("{question}", "{input}")
    
    # Fallback de segurança
    if "{context}" not in raw_prompt:
        raw_prompt = "Contexto: {context}\n\nPergunta: {input}\n\nResposta:"

    prompt = ChatPromptTemplate.from_template(raw_prompt)
    
    # Injeta o idioma se necessário
    if "{language}" in raw_prompt:
        prompt = prompt.partial(language=lang_code)

    # 4. Criação da Chain (Isso substitui o RetrievalQA)
    # Primeiro criamos a chain que combina documentos com o LLM
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # Depois criamos a chain que busca os documentos e passa para a anterior
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                # Na nova sintaxe, passamos "input" em vez de "query"
                response = rag_chain.invoke({"input": user_input})
                
                answer = response["answer"]
                sources = response["context"]

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
