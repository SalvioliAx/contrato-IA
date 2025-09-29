import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# --- Constants ---
MODEL_NAME = "gemini-2.5-flash"

def render_chat_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Renderiza a aba de Chat, permitindo conversas RAG (Retrieval Augmented Generation)
    com base nos documentos carregados, e exibindo as fontes.
    """
    st.header(texts.get("chat_header", "💬 Chat com Contratos"))

    # Verifica se o vector store está pronto
    if "vector_store_atual" not in st.session_state:
        st.info(texts.get("chat_info_load_docs", "Carregue documentos na barra lateral para iniciar o chat."))
        return

    # Inicializa o histórico do chat se não existir
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": texts.get("chat_welcome_message", "Olá! Seus documentos estão prontos. Faça sua pergunta.")
        }]

    # 1. Setup LLM and Retriever
    try:
        llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=google_api_key,
            temperature=0.1
        )
        retriever = st.session_state["vector_store_atual"].as_retriever()
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo ou retriever: {e}")
        return

    # 2. Setup Prompt and RAG Chain
    # CORREÇÃO: Alterado {question} para {query} no prompt para corresponder à chave
    # usada na invocação da chain (chain.invoke({'query': user_input})).
    prompt_template_str = (
        "Você é um assistente de IA amigável e útil, especializado em análise de documentos contratuais. "
        "Responda à PERGUNTA com base APENAS no CONTEXTO fornecido pelos documentos. "
        "Se o contexto não contiver a resposta, informe que não encontrou a informação nos documentos.\\n\\n"
        "CONTEXTO:\\n{context}\\n\\n" 
        "PERGUNTA: {query}\\n\\n" # <-- A chave de input agora é 'query'
        "RESPOSTA:"
    )
    prompt = PromptTemplate.from_template(prompt_template_str)

    # Cria a cadeia RAG
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True, # Essencial para obter as fontes
        chain_type_kwargs={"prompt": prompt}
    )

    # 3. Renderiza as mensagens do histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Expansor para mostrar as fontes da resposta da IA
            if msg.get("sources"):
                with st.expander(texts.get("chat_view_sources", "Ver Fontes")):
                    for doc in msg["sources"]:
                        texto_fonte = doc.page_content
                        metadata = doc.metadata
                        # Usando get para lidar com a ausência de chaves
                        source_info = metadata.get('source', 'N/A')
                        page_info = metadata.get('page', 'N/A')
                        st.markdown(f"**Fonte:** {source_info} (Página {page_info})")
                        st.code(texto_fonte[:500] + '...', language='markdown') # Limita o tamanho do snippet

    # 4. Handle user input
    if user_input := st.chat_input(texts.get("chat_input_placeholder", "Pergunte algo sobre seus contratos...")):
        # Adiciona a pergunta do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Exibe a pergunta do usuário
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            # Usa a chave de tradução para o spinner
            with st.spinner(texts.get("chat_loading", "Analisando documentos...")): 
                try:
                    # Invoca o RAG chain. 'query' é a chave que RetrievalQA espera.
                    result = chain.invoke({"query": user_input})
                    resposta = result["result"]
                    fontes = result["source_documents"]

                    # Adiciona a resposta e as fontes ao histórico
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": resposta,
                        "sources": fontes 
                    })
                    # Força o rerender para exibir a nova mensagem imediatamente
                    st.rerun()

                except Exception as e:
                    # Usa a chave de tradução para a mensagem de erro
                    error_msg = texts.get("chat_error_response", "Ocorreu um erro ao gerar a resposta.")
                    st.error(f"{error_msg}: {e}")
