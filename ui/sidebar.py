import streamlit as st
from services.collections import (
    listar_colecoes_salvas, salvar_colecao_atual, carregar_colecao
)
from services.document_loader import obter_vector_store_de_uploads

def render_sidebar(embeddings_global, google_api_key, texts):
    """
    Renderiza a barra lateral, agora com textos localizados e spinner traduzido.
    """
    st.sidebar.header(texts["sidebar_header"])

    # Lógica de seleção de idioma movida para app.py

    uploaded_files = st.sidebar.file_uploader(
        texts["sidebar_uploader_label"], type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        if st.sidebar.button(texts["sidebar_process_button"], use_container_width=True):
            if google_api_key and embeddings_global:
                with st.spinner(texts["sidebar_spinner_processing"]):
                    vs, nomes = obter_vector_store_de_uploads(uploaded_files, embeddings_global, google_api_key)
                if vs:
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes
                    st.session_state.arquivos_pdf_originais = uploaded_files
                    st.session_state.messages = [] # Limpa o chat
                    if "dados_extraidos" in st.session_state:
                         del st.session_state.dados_extraidos # Limpa dados do dashboard
                    st.rerun()
            else:
                st.sidebar.error(texts["error_api_key"])


    st.sidebar.markdown("---")
    
    # Salvar Coleção
    if st.session_state.get("arquivos_pdf_originais"):
        colecao_salvar = st.sidebar.text_input(texts["sidebar_save_collection_label"])
        if st.sidebar.button(texts["sidebar_save_collection_button"], use_container_width=True):
            if "vector_store_atual" in st.session_state:
                salvar_colecao_atual(
                    colecao_salvar,
                    st.session_state.vector_store_atual,
                    st.session_state.nomes_arquivos_atuais
                )
    else:
        st.sidebar.info(texts["sidebar_save_collection_warning"])


    # Carregar Coleção
    colecoes_existentes = listar_colecoes_salvas()
    if colecoes_existentes:
        colecao_selecionada = st.sidebar.selectbox(
            texts["sidebar_load_collection_label"],
            options=[""] + colecoes_existentes, # Adiciona opção vazia
            format_func=lambda x: texts["sidebar_load_collection_placeholder"] if x == "" else x
        )
        if st.sidebar.button(texts["sidebar_load_collection_button"], use_container_width=True):
            if colecao_selecionada and google_api_key and embeddings_global:
                vs, nomes = carregar_colecao(colecao_selecionada, embeddings_global)
                if vs:
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes
                    st.session_state.arquivos_pdf_originais = None
                    st.session_state.messages = []
                    if "dados_extraidos" in st.session_state:
                         del st.session_state.dados_extraidos
                    st.rerun()
            else:
                st.sidebar.error(texts["sidebar_load_collection_error"])

