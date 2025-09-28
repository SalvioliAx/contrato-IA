import streamlit as st
from src.services import collection_manager, document_processor
from src.utils import reset_analysis_data

def display_language_selector(t):
    """Exibe os botões de seleção de idioma na barra lateral."""
    st.sidebar.subheader(t("sidebar.language_header"))
    
    # Cria três colunas para os botões de idioma
    cols = st.sidebar.columns(3)
    with cols[0]:
        if st.button(t("ui.language_buttons.pt"), use_container_width=True, key="lang_pt"):
            st.session_state.language = "pt"
            st.rerun()
    with cols[1]:
        if st.button(t("ui.language_buttons.en"), use_container_width=True, key="lang_en"):
            st.session_state.language = "en"
            st.rerun()
    with cols[2]:
        if st.button(t("ui.language_buttons.es"), use_container_width=True, key="lang_es"):
            st.session_state.language = "es"
            st.rerun()

def handle_upload_section(api_key, embeddings_model, t):
    """Lida com a secção de upload de novos ficheiros PDF."""
    arquivos_pdf_upload = st.sidebar.file_uploader(
        t("sidebar.file_uploader_label"),
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader"
    )

    if not arquivos_pdf_upload:
        st.sidebar.info(t("sidebar.no_files_selected"))
        st.session_state.arquivos_pdf_originais = []
        return

    st.session_state.arquivos_pdf_originais = arquivos_pdf_upload

    if st.sidebar.button(t("sidebar.process_button"), use_container_width=True):
        if not (api_key and embeddings_model):
            st.sidebar.error(t("errors.api_key_or_embeddings_not_configured_short"))
            return

        with st.spinner(t("info.processing_and_indexing")):
            vs, nomes_arqs = document_processor.obter_vector_store_de_uploads(
                arquivos_pdf_upload, embeddings_model, api_key, t
            )

        if vs and nomes_arqs:
            reset_analysis_data()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = nomes_arqs
            st.session_state.colecao_ativa = None
            st.session_state.messages = []
            st.sidebar.success(t("sidebar.success_processed_files", count=len(nomes_arqs)))
            st.rerun()
        else:
            st.sidebar.error(t("sidebar.error_processing_files"))

def handle_collection_section(embeddings_model, t):
    """Lida com a secção de carregamento de coleções existentes."""
    colecoes_disponiveis = collection_manager.listar_colecoes_salvas()
    if not colecoes_disponiveis:
        st.sidebar.info(t("sidebar.no_collections_saved"))
        return

    colecao_selecionada = st.sidebar.selectbox(
        t("sidebar.collection_selectbox_label"),
        colecoes_disponiveis,
        index=None,
        placeholder=t("sidebar.collection_selectbox_placeholder")
    )

    if st.sidebar.button(t("sidebar.load_collection_button"), use_container_width=True):
        if not colecao_selecionada:
            st.sidebar.warning(t("sidebar.warning_no_collection_selected"))
            return

        if embeddings_model:
            vs, nomes_arqs = collection_manager.carregar_colecao(colecao_selecionada, embeddings_model, t)
            if vs and nomes_arqs:
                reset_analysis_data()
                st.session_state.vector_store = vs
                st.session_state.nomes_arquivos = nomes_arqs
                st.session_state.colecao_ativa = colecao_selecionada
                st.session_state.arquivos_pdf_originais = None
                st.session_state.messages = []
                st.rerun()
        else:
            st.sidebar.error(t("errors.api_key_or_embeddings_not_configured_short"))

def handle_save_collection_section(t):
    """Lida com a secção para salvar a coleção atual."""
    if st.session_state.get("vector_store") and st.session_state.get("arquivos_pdf_originais"):
        st.sidebar.markdown("---")
        st.sidebar.subheader(t("sidebar.save_collection_subheader"))
        nome_nova_colecao = st.sidebar.text_input(t("sidebar.new_collection_name_label"))
        
        if st.sidebar.button(t("sidebar.save_collection_button"), use_container_width=True):
            if nome_nova_colecao and st.session_state.get("nomes_arquivos"):
                collection_manager.salvar_colecao_atual(
                    nome_nova_colecao,
                    st.session_state.vector_store,
                    st.session_state.nomes_arquivos,
                    t
                )
            else:
                st.sidebar.warning(t("sidebar.warning_give_name_to_collection"))

def display_sidebar(api_key, embeddings_model, t):
    """Renderiza a barra lateral completa."""
    with st.sidebar:
        st.header(t("sidebar.header"))

        # Adiciona o seletor de idioma
        display_language_selector(t)
        st.sidebar.markdown("---")

        modo_documento = st.radio(
            t("sidebar.doc_load_mode_label"),
            [t("sidebar.doc_load_mode_upload"), t("sidebar.doc_load_mode_collection")],
            index=0,
            key="doc_mode_radio"
        )

        st.markdown("---")

        if modo_documento == t("sidebar.doc_load_mode_upload"):
            handle_upload_section(api_key, embeddings_model, t)
        else:
            handle_collection_section(embeddings_model, t)

        handle_save_collection_section(t)

        st.sidebar.markdown("---")
        if st.session_state.get("colecao_ativa"):
            st.sidebar.markdown(f"**{t('sidebar.active_collection')}:** `{st.session_state.colecao_ativa}`")
        elif st.session_state.get("nomes_arquivos"):
            st.sidebar.markdown(f"**{t('sidebar.loaded_files')}:** {len(st.session_state.nomes_arquivos)}")

