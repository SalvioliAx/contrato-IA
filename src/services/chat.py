import streamlit as st
from src.services import chat
from src.utils import formatar_chat_para_markdown

def display_chat_tab(t):
    """Renderiza a aba de Chat Interativo."""
    st.header(t("chat.header"))

    if not st.session_state.get("messages"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": t("chat.initial_message",
                         collection=st.session_state.get('colecao_ativa', 'upload atual'),
                         count=len(st.session_state.get("nomes_arquivos", [])))
        })

    # Renderiza o histórico do chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander(t("chat.view_sources_expander")):
                    if message.get("clausula_citada"):
                        st.markdown(f"**{t('chat.main_reference')}:** {message['clausula_citada']}")
                        st.markdown("---")
                    
                    for doc_fonte in message["sources"]:
                        # Lógica para exibir fontes (pode ser aprimorada)
                        st.caption(f"Fonte: {doc_fonte.metadata.get('source', 'N/A')} (Pág: {doc_fonte.metadata.get('page', 'N/A')})")
                        st.markdown(f"> {doc_fonte.page_content[:300]}...")
                        st.markdown("---")

    # Botão de exportar
    if len(st.session_state.messages) > 1:
        chat_exportado_md = formatar_chat_para_markdown(st.session_state.messages, t)
        st.download_button(
            label=t("chat.export_button"),
            data=chat_exportado_md,
            file_name="conversa_contratos.md",
            mime="text/markdown"
        )
    
    st.markdown("---")

    # Input do utilizador
    if prompt := st.chat_input(t("chat.input_placeholder")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner(t("chat.thinking_spinner")):
            try:
                resposta_ia = chat.processar_pergunta_chat(
                    prompt,
                    st.session_state.vector_store,
                    st.session_state.language,
                    t
                )
                st.session_state.messages.append(resposta_ia)
            except Exception as e:
                st.error(t("errors.chat_qa_failed", error=e))
                st.session_state.messages.append({"role": "assistant", "content": t("errors.chat_processing_error")})
        
        st.rerun()

