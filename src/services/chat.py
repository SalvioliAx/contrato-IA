import streamlit as st
from datetime import datetime
from src.services.chat import processar_pergunta_chat
from src.utils import formatar_chat_para_markdown

def display_chat_tab(t):
    """Renderiza a aba de Chat Interativo com exibição de fontes e erros."""
    st.header(t("chat.header"))

    if 'chat_error' in st.session_state and st.session_state.chat_error:
        st.error(t("errors.detailed_error_intro"))
        st.code(st.session_state.chat_error, language='text')
        if st.button(t("errors.clear_error_button")):
            del st.session_state['chat_error']
            st.rerun()

    # CORREÇÃO: Garante que 'nomes_arquivos' tenha um valor padrão (lista vazia)
    # para evitar o TypeError: len() of NoneType na inicialização.
    if not st.session_state.get("messages"):
        nomes_arquivos = st.session_state.get('nomes_arquivos', [])
        st.session_state.messages = [{
            "role": "assistant",
            "content": t("chat.initial_message",
                         collection=st.session_state.get('colecao_ativa', 'nova'),
                         count=len(nomes_arquivos))
        }]

    # Renderiza o histórico do chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander(t("chat.view_sources_expander")):
                    if message.get("clausula_citada") and "não aplicável" not in message["clausula_citada"].lower():
                         st.markdown(f"**{t('chat.main_reference')}:** {message['clausula_citada']}")
                         st.markdown("---")
                    
                    for doc in message["sources"]:
                        texto_fonte = doc.page_content
                        sentenca_chave = message.get("sentenca_chave")
                        
                        if sentenca_chave and sentenca_chave in texto_fonte:
                            texto_fonte_html = texto_fonte.replace(sentenca_chave, f"<mark>{sentenca_chave}</mark>", 1)
                            st.markdown(texto_fonte_html, unsafe_allow_html=True)
                        else:
                            st.markdown(texto_fonte)
                        
                        source_name = doc.metadata.get('source', 'N/A')
                        page_num = doc.metadata.get('page', 'N/A')
                        st.caption(f"{t('chat.source_caption', source=source_name, page=page_num)}")
                        st.markdown("---")

    if len(st.session_state.messages) > 1:
        chat_exportado = formatar_chat_para_markdown(st.session_state.messages, t)
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label=t("chat.export_button"),
            data=chat_exportado,
            file_name=f"chat_contratia_{agora}.md",
            mime="text/markdown"
        )

    st.markdown("---")
    prompt_disabled = bool(st.session_state.get('chat_error'))
    prompt = st.chat_input(t("chat.input_placeholder"), key="chat_input_main", disabled=prompt_disabled)
    
    if prompt:
        processar_pergunta_chat(prompt, st.session_state.vector_store, t)
        st.rerun()

