import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def render_chat_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Chat, agora com a funcionalidade "Ver Fontes".
    """
    st.header("💬 Chat com Contratos")

    # Verifica se o vector store está pronto
    if "vector_store_atual" not in st.session_state:
        st.info("Carregue documentos na barra lateral para iniciar o chat.")
        return

    # Inicializa o histórico do chat se não existir
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Olá! Seus documentos estão prontos. Faça sua pergunta."
        }]

    # Renderiza as mensagens do histórico, incluindo o expansor de fontes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # ADICIONADO: Expansor para mostrar as fontes da resposta da IA
            if msg.get("sources"):
                with st.expander("Ver Fontes"):
                    for doc in msg["sources"]:
                        texto_fonte = doc.page_content
                        metadata = doc.metadata
                        st.markdown(f"**Fonte:** `{metadata.get('source', 'N/A')}` (Página: {metadata.get('page', 'N/A')})")
                        st.markdown(f"> {texto_fonte.strip()}")
                        st.markdown("---")

    # Input do usuário
    user_input = st.chat_input("Digite sua pergunta sobre os contratos...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
        retriever = st.session_state.vector_store_atual.as_retriever(search_kwargs={"k": 5})
        
        # Template de prompt para guiar a IA a dar respostas baseadas no contexto
        prompt_template_str = (
            "Use os trechos de contexto para responder à pergunta. Responda de forma completa e explicativa com base no contexto.\n"
            "Se o contexto não contiver a resposta, informe que não encontrou a informação nos documentos.\n\n"
            "CONTEXTO:\n{context}\n\n"
            "PERGUNTA: {question}\n\n"
            "RESPOSTA:"
        )
        prompt = PromptTemplate.from_template(prompt_template_str)

        # MODIFICADO: Usando RetrievalQA para retornar os documentos fonte
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True, # Essencial para obter as fontes
            chain_type_kwargs={"prompt": prompt}
        )

        with st.chat_message("assistant"):
            with st.spinner("Analisando documentos..."):
                try:
                    result = chain.invoke({"query": user_input})
                    resposta = result["result"]
                    fontes = result["source_documents"]

                    # Adiciona a resposta e as fontes ao histórico
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": resposta,
                        "sources": fontes # Armazena as fontes
                    })
                    # Força o rerender para exibir a nova mensagem imediatamente
                    st.rerun()

                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
