import streamlit as st
import re
from datetime import datetime
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from core.utils import get_llm, format_chat_for_markdown

def render():
    st.header("Converse com seus documentos")
    
    # Mensagem inicial da IA
    if not st.session_state.messages:
        collection_name = st.session_state.get('colecao_ativa', 'atual')
        num_files = len(st.session_state.get('nomes_arquivos', []))
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Olá! Documentos da coleção '{collection_name}' prontos ({num_files} arquivo(s)). Qual sua pergunta?"
        })

    # Renderiza o histórico do chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Ver Fontes"):
                    for doc in message["sources"]:
                        st.markdown(f"**Fonte:** `{doc.metadata.get('source', 'N/A')}` (Pág: {doc.metadata.get('page', 'N/A')})")
                        st.info(f"> {doc.page_content[:500]}...")

    # Botão de exportação
    if len(st.session_state.messages) > 1:
        chat_md = format_chat_for_markdown(st.session_state.messages)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Exportar Conversa",
            data=chat_md,
            file_name=f"conversa_contratos_{now}.md",
            mime="text/markdown"
        )
    
    st.markdown("---")
    
    # Entrada do usuário
    if prompt := st.chat_input("Faça sua pergunta sobre os contratos..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Pesquisando e pensando..."):
                response = get_ai_response(prompt)
                st.session_state.messages.append(response)
        st.rerun()

def get_ai_response(question: str) -> dict:
    """Obtém uma resposta do modelo de IA com base na pergunta e no contexto dos documentos."""
    llm = get_llm(temperature=0.2)
    vector_store = st.session_state.get("vector_store")

    if not llm or not vector_store:
        return {"role": "assistant", "content": "Erro: LLM ou Vector Store não estão disponíveis."}

    template = (
        "Você é um assistente analítico. Use os trechos de contexto para responder à pergunta de forma completa. "
        "Se o contexto não contiver a resposta, informe que não encontrou a informação nos documentos.\n\n"
        "CONTEXTO:\n{context}\n\n"
        "PERGUNTA: {question}\n\n"
        "RESPOSTA:"
    )
    prompt_template = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 7}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

    try:
        result = qa_chain.invoke({"query": question})
        return {
            "role": "assistant",
            "content": result["result"],
            "sources": result["source_documents"]
        }
    except Exception as e:
        st.error(f"Erro durante a execução da cadeia de QA: {e}")
        return {"role": "assistant", "content": "Desculpe, ocorreu um erro ao processar sua pergunta."}
