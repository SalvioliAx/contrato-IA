import streamlit as st

from services.collections import (
    listar_colecoes_salvas,
    salvar_colecao_atual,
    carregar_colecao
)

from services.document_loader import obter_vector_store_de_uploads


def render_sidebar(embeddings_global, google_api_key, texts):
    """
    Renderiza a barra lateral com textos traduzidos e lógica de upload/carregamento.
    """
    st.sidebar.header(texts["sidebar_header"])

    # ---------------------------------------------------------
    # UPLOAD DE DOCUMENTOS
    # ---------------------------------------------------------
    uploaded_files = st.sidebar.file_uploader(
        label=texts["sidebar_uploader_label"],
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        process_button = st.sidebar.button(
            texts["sidebar_process_button"],
            use_container_width=True
        )

        if process_button:
            if google_api_key and embeddings_global:
                with st.spinner(texts["sidebar_spinner_processing"]):
                    vs, nomes = obter_vector_store_de_uploads(
                        uploaded_files, embeddings_global, google_api_key
                    )

                if vs:
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes
                    st.session_state.arquivos_pdf_originais = uploaded_files

                    # Limpa chat
                    st.session_state.messages = []

                    # Limpa dados do dashboard
                    st.session_state.pop("dados_extraidos", None)

                    st.rerun()
            else:
                st.sidebar.error(texts["error_api_key"])

    st.sidebar.markdown("---")

    # ---------------------------------------------------------
    # SALVAR COLEÇÃO
    # ---------------------------------------------------------
    if st.session_state.get("arquivos_pdf_originais"):
        colecao_nome = st.sidebar.text_input(texts["sidebar_save_collection_label"])

        salvar_button = st.sidebar.button(
            texts["sidebar_save_collection_button"],
            use_container_width=True
        )

        if salvar_button and "vector_store_atual" in st.session_state:
            salvar_colecao_atual(
                colecao_nome,
                st.session_state.vector_store_atual,
                st.session_state.nomes_arquivos_atuais
            )
    else:
        st.sidebar.info(texts["sidebar_save_collection_warning"])

    # ---------------------------------------------------------
    # CARREGAR COLEÇÃO
    # ---------------------------------------------------------
    colecoes = listar_colecoes_salvas()

    if colecoes:
        colecao_escolhida = st.sidebar.selectbox(
            label=texts["sidebar_load_collection_label"],
            options=[""] + colecoes,
            format_func=lambda x: (
                texts["sidebar_load_collection_placeholder"] if x == "" else x
            )
        )

        load_button = st.sidebar.button(
            texts["sidebar_load_collection_button"],
            use_container_width=True
        )

        if load_button:
            if colecao_escolhida and google_api_key and embeddings_global:
                vs, nomes = carregar_colecao(colecao_escolhida, embeddings_global)

                if vs:
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes

                    # Remove PDFs carregados anteriormente
                    st.session_state.arquivos_pdf_originais = None

                    # Limpa chat
                    st.session_state.messages = []

                    # Remove informações calculadas anteriormente
                    st.session_state.pop("dados_extraidos", None)

                    st.rerun()
            else:
                st.sidebar.error(texts["sidebar_load_collection_error"])
