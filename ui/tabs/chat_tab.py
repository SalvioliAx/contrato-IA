import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
# IMPORTANTE: Usar a chain de documentos correta para LCEL
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["chat_header"])

    # 1. Verificação do Vector Store
    if "vector_store_atual" not in st.session_state:
        st.info(texts["chat_info_load_docs"])
        return

    # 2. Inicialização do Histórico
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": texts["chat_welcome_message"]}
        ]

    # 3. Renderização das Mensagens Anteriores
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Renderizar fontes se existirem
            if msg.get("sources"):
                with st.expander(texts["chat_expander_sources"]):
                    for doc in msg["sources"]:
                        metadata = doc.metadata
                        st.markdown(
                            f"**{texts['chat_source_label']}** `{metadata.get('source', 'N/A')}` "
                            f"({texts['chat_page_label']} {metadata.get('page', 'N/A')})"
                        )
                        # Limita o texto da fonte visualmente para não poluir
                        snippet = doc.page_content.strip()[:300] + "..."
                        st.markdown(f"> {snippet}")
                        st.markdown("---")

    # 4. Input do Usuário
    user_input = st.chat_input(texts["chat_input_placeholder"])
    if not user_input:
        return

    # Adiciona input do usuário ao histórico visual imediatamente
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- INÍCIO DA LÓGICA RAG ---
    
    # CORREÇÃO 1: Modelo Válido (gemini-1.5-pro ou gemini-1.5-flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        temperature=0.1,
        google_api_key=google_api_key
    )

    retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})

    # CORREÇÃO 2: Garantir que o prompt tenha {context}
    # O prompt DEVE ter {context} e {input} para o create_stuff_documents_chain funcionar
    raw_prompt = texts.get("chat_prompt", "Contexto: {context} \n\n Pergunta: {input}")
    
    # Se o prompt do seu arquivo de textos não tiver {context}, forçamos um padrão seguro
    if "{context}" not in raw_prompt:
        raw_prompt = "Use o seguinte contexto para responder à pergunta:\n{context}\n\nPergunta: {input}"

    prompt = ChatPromptTemplate.from_template(raw_prompt)
    
    # Se precisar injetar o idioma, faça partial aqui, mas garanta que o prompt aceita {language}
    if "{language}" in raw_prompt:
        prompt = prompt.partial(language=lang_code)

    # CORREÇÃO 3: Usar create_stuff_documents_chain (Moderno) ao invés de StuffDocumentsChain (Legado)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    with st.chat_message("assistant"):
        with st.spinner(texts["chat_spinner_thinking"]):
            try:
                # O novo padrão LCEL espera 'input', não 'question' ou outros
                result = rag_chain.invoke({"input": user_input})
                
                answer = result["answer"]
                sources = result.get("context", [])

                st.markdown(answer)

                # Salvar no histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"{texts['chat_error']} {e}")
                # Imprimir o erro no console do Streamlit Cloud para debug
                print(f"Erro detalhado: {e}")
