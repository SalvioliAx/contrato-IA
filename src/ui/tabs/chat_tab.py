import streamlit as st
from datetime import datetime
from services.chat import processar_pergunta_chat
from utils import formatar_chat_para_markdown

def display_chat_tab(t):
    """Renderiza a aba de Chat Interativo com exibição de erros de depuração."""
    st.header(t("chat.header"))

    # Exibe um erro persistente, se houver um
    if 'chat_error' in st.session_state and st.session_state.chat_error:
        st.error(t("errors.detailed_error_intro"))
        st.code(st.session_state.chat_error, language='text')
        if st.button(t("errors.clear_error_button")):
            del st.session_state.chat_error
            st.rerun()

    # Mensagem inicial e histórico do chat ...
    if not st.session_state.messages:
        # ... (código da mensagem inicial)
        pass
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # ... (código para exibir fontes)

    if len(st.session_state.messages) > 1:
        # ... (código do botão de exportar)
        pass

    st.markdown("---")
    # Desativa o input se houver um erro ativo
    prompt = st.chat_input(
        t("chat.input_placeholder"), 
        key="chat_input_main", 
        disabled=('chat_error' in st.session_state and st.session_state.chat_error is not None)
    )
    if prompt:
        processar_pergunta_chat(prompt, st.session_state.vector_store, t)
        st.rerun()

