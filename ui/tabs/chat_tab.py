import streamlit as st
# Importação do modelo
from langchain_google_genai import ChatGoogleGenerativeAI
# Importação do PromptTemplate (Versão Core)
from langchain_core.prompts import PromptTemplate

# --- CORREÇÃO DA IMPORTAÇÃO DA CHAIN ---
# Tenta importar do caminho padrão, se falhar, vai no caminho explícito
try:
    from langchain.chains import RetrievalQA
except ImportError:
    from langchain.chains.retrieval_qa.base import RetrievalQA
# ---------------------------------------

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    # 1. Verifica se documentos foram processados
    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    # 2. Inicializa histórico do chat
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

    # --- LÓGICA RAG (Modo Legacy/Restaurado) ---
    
    # Mantendo gemini-2.5-pro conforme solicitado
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        google_api_key=google_api_key
    )

    # Configuração do Prompt (Adaptação para RetrievalQA)
    prompt_template = texts.get("chat_prompt", "")
    
    # O RetrievalQA 'antigo' EXIGE a variável {question}. 
    if "{question}" not in prompt_template and "{input}" in prompt_template:
        prompt_template = prompt_template.replace("{input}", "{question}")
    
    # Fallback caso o prompt esteja vazio
    if "{question}" not in prompt_template:
        prompt_template = "Contexto: {context}\n\nPergunta: {question}\n\nResposta em {language}:"

    # Criação do Prompt Template
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"],
        partial_variables={"language": lang_code} if "{language}" in prompt_template else {}
    )

    # Configuração da Chain (RetrievalQA)
    # Nota: chain_type="stuff" usa StuffDocumentsChain internamente
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                # O RetrievalQA usa a chave "query" ou "question" no invoke
                result = qa_chain.invoke({"query": user_input})
                
                answer = result["result"]
                sources = result["source_documents"]

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
