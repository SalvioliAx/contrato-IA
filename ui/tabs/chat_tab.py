import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# --- BLOCO DE IMPORTAÇÃO UNIVERSAL (À PROVA DE ERROS) ---
# Tenta importar o jeito novo. Se falhar, importa o jeito velho.
try:
    # Tenta importar os componentes da versão 0.1+ (Moderna)
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    VERSAO_MODERNA = True
except ImportError:
    # Se falhar, usa os componentes da versão antiga (Legacy)
    # Isso garante que funcione mesmo se o requirements.txt não atualizar
    try:
        from langchain.chains import RetrievalQA
    except ImportError:
        from langchain.chains.retrieval_qa.base import RetrievalQA
    
    # Tenta importar PromptTemplate do lugar antigo ou novo
    try:
        from langchain.prompts import PromptTemplate
    except ImportError:
        from langchain_core.prompts import PromptTemplate
        
    VERSAO_MODERNA = False
# --------------------------------------------------------

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    # 1. Verifica Vector Store
    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    # 2. Histórico
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
                        st.markdown(f"**{texts['chat_source_label']}** `{metadata.get('source', 'N/A')}`")
                        st.caption(f"{doc.page_content[:300]}...")
                        st.markdown("---")

    # 3. Input
    user_input = st.chat_input(texts["chat_input_placeholder"])
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 4. LLM (Modelo mantido 2.5-pro a seu pedido)
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1,
            google_api_key=google_api_key
        )
    except Exception as e:
        st.error(f"Erro ao iniciar modelo: {e}")
        return

    retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                # --- LÓGICA HÍBRIDA ---
                if VERSAO_MODERNA:
                    # >>> CAMINHO NOVO (LangChain 0.1+) <<<
                    raw_prompt = texts.get("chat_prompt", "")
                    raw_prompt = raw_prompt.replace("{question}", "{input}") # Adapta variável
                    
                    if "{context}" not in raw_prompt:
                         raw_prompt = "Contexto: {context}\n\nPergunta: {input}\n\nResposta:"
                    
                    prompt = ChatPromptTemplate.from_template(raw_prompt)
                    if "{language}" in raw_prompt:
                        prompt = prompt.partial(language=lang_code)

                    question_answer_chain = create_stuff_documents_chain(llm, prompt)
                    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
                    
                    response = rag_chain.invoke({"input": user_input})
                    answer = response["answer"]
                    sources = response.get("context", [])

                else:
                    # >>> CAMINHO ANTIGO (LangChain Legacy) <<<
                    # O servidor está com versão antiga, usamos RetrievalQA
                    prompt_template_str = texts.get("chat_prompt", "")
                    # O antigo exige {question}
                    if "{question}" not in prompt_template_str and "{input}" in prompt_template_str:
                        prompt_template_str = prompt_template_str.replace("{input}", "{question}")
                    
                    if "{question}" not in prompt_template_str:
                         prompt_template_str = "Contexto: {context}\n\nPergunta: {question}\n\nResposta:"

                    PROMPT = PromptTemplate(
                        template=prompt_template_str,
                        input_variables=["context", "question"],
                        partial_variables={"language": lang_code} if "{language}" in prompt_template_str else {}
                    )

                    qa_chain = RetrievalQA.from_chain_type(
                        llm=llm,
                        chain_type="stuff",
                        retriever=retriever,
                        return_source_documents=True,
                        chain_type_kwargs={"prompt": PROMPT}
                    )
                    
                    result = qa_chain.invoke({"query": user_input})
                    answer = result["result"]
                    sources = result["source_documents"]

                # Exibição do Resultado (Igual para os dois)
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
                print(f"DEBUG ERRO: {e}") # Ajuda a ver o erro no log do servidor
