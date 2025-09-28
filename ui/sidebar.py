import streamlit as st
from services.collections import (
    listar_colecoes_salvas, salvar_colecao_atual, carregar_colecao
)
from services.document_loader import obter_vector_store_de_uploads

def render_sidebar(embeddings_global, google_api_key, texts):
    """
    Renderiza a barra lateral, agora usando textos do dicionário de localização.
    """
    st.sidebar.header(texts["sidebar_header"])

    uploaded_files = st.sidebar.file_uploader(
        texts["sidebar_uploader_label"], type=["pdf"], accept_multiple_files=True, key="upload_pdf"
    )

    nome_colecao_salvar = st.sidebar.text_input(texts["sidebar_save_collection_label"])
    if st.sidebar.button(texts["sidebar_save_collection_button"]):
        if "vector_store_atual" in st.session_state and uploaded_files:
            salvar_colecao_atual(
                nome_colecao_salvar,
                st.session_state.vector_store_atual,
                st.session_state.nomes_arquivos_atuais
            )
        else:
            st.sidebar.warning(texts["sidebar_save_collection_warning"])

    st.sidebar.markdown("---")
    colecoes_existentes = listar_colecoes_salvas()
    if colecoes_existentes:
        colecao_selecionada = st.sidebar.selectbox(
            texts["sidebar_load_collection_label"],
            colecoes_existentes,
            index=None,
            placeholder=texts["sidebar_load_collection_placeholder"]
        )
        if st.sidebar.button(texts["sidebar_load_collection_button"]):
            if colecao_selecionada and embeddings_global:
                vs, nomes = carregar_colecao(colecao_selecionada, embeddings_global)
                if vs:
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes
                    st.session_state.arquivos_pdf_originais = None
                    st.session_state.messages = []
                    st.rerun()
            else:
                st.sidebar.error(texts["sidebar_load_collection_error"])

    if uploaded_files:
        if st.sidebar.button(texts["sidebar_process_button"]):
            vs, nomes = obter_vector_store_de_uploads(uploaded_files, embeddings_global, google_api_key)
            if vs:
                st.session_state.vector_store_atual = vs
                st.session_state.nomes_arquivos_atuais = nomes
                st.session_state.arquivos_pdf_originais = uploaded_files
                st.session_state.messages = []
                st.rerun()

