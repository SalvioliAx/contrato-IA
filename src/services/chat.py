import streamlit as st
from datetime import datetime
from src.services import chat
from src.utils import formatar_chat_para_markdown

def render(t):
    """Renderiza a aba de Chat Interativo."""
    st.header(t("chat.header"))

    # Mensagem inicial se o chat estiver vazio
    if not st.session_state.messages:
        colecao_info = st.session_state.get('colecao_ativa', t("chat.this_session"))
        num_arquivos = len(st.session_state.get("nomes_arquivos", []))
        st.session_state.messages.append({
            "role": "assistant",
            "content": t("chat.initial_message", collection=colecao_info, count=num_arquivos)
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
                    
                    for doc in message["sources"]:
                        texto_fonte = doc.page_content
                        # Destaca o trecho relevante se encontrado
                        if message.get("sentenca_chave") and message["sentenca_chave"] in texto_fonte:
                            texto_html = texto_fonte.replace(message["sentenca_chave"], f"<mark>{message['sentenca_chave']}</mark>", 1)
                            st.markdown(texto_html, unsafe_allow_html=True)
                        else:
                            st.markdown(texto_fonte)
                        
                        source = doc.metadata.get('source', 'N/A')
                        page = doc.metadata.get('page', 'N/A')
                        st.caption(t("chat.source_caption", source=source, page=page))
                        st.markdown("---")

    # Botão de exportação
    if len(st.session_state.messages) > 1:
        chat_md = formatar_chat_para_markdown(st.session_state.messages, t)
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label=t("chat.export_button"),
            data=chat_md,
            file_name=f"conversa_contratos_{agora}.md",
            mime="text/markdown"
        )
    
    st.markdown("---")
    # Input do utilizador
    prompt = st.chat_input(t("chat.input_placeholder"), key="chat_input_main")
    if prompt:
        chat.handle_chat_submission(prompt, st.session_state.vector_store, t)
        st.rerun()
