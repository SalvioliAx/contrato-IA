import streamlit as st
from src.services import collection_manager, document_processor
from src.utils import reset_analysis_data

def handle_upload_section(api_key, embeddings_model, t):
    """Lida com a secção de upload de novos ficheiros PDF."""
    arquivos_pdf_upload = st.file_uploader(
        t("sidebar.file_uploader_label"),
        type="pdf",
        accept_multiple_files=True,
        key="uploader_sidebar"
    )
    if not arquivos_pdf_upload:
        st.info(t("sidebar.no_files_selected"))

    if st.button(t("sidebar.process_button"), key="btn_proc_upload", use_container_width=True):
        if not arquivos_pdf_upload:
            st.warning(t("sidebar.warning_no_files_to_process"))
            return

        if not (api_key and embeddings_model):
            st.error(t("errors.api_key_or_embeddings_not_configured_short"))
            return
        
        with st.spinner(t("info.processing_and_indexing")):
            vs, nomes_arqs = document_processor.obter_vector_store_de_uploads(
                arquivos_pdf_upload, embeddings_model, api_key, t
            )
        
        if vs and nomes_arqs:
            reset_analysis_data()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = nomes_arqs
            st.session_state.arquivos_pdf_originais = arquivos_pdf_upload
            st.session_state.colecao_ativa = None
            st.session_state.messages = []
            st.success(t("sidebar.success_processed_files", count=len(nomes_arqs)))
            st.rerun()
        else:
            st.error(t("sidebar.error_processing_files"))

def handle_collection_section(embeddings_model, t):
    """Lida com a secção de carregamento de coleções existentes."""
    colecoes = collection_manager.listar_colecoes_salvas()
    if not colecoes:
        st.info(t("sidebar.no_collections_saved"))
        return

    colecao_selecionada = st.selectbox(
        t("sidebar.collection_selectbox_label"),
        colecoes,
        key="select_colecao",
        index=None,
        placeholder=t("sidebar.collection_selectbox_placeholder")
    )
    if st.button(t("sidebar.load_collection_button"), key="btn_load_colecao", use_container_width=True):
        if not colecao_selecionada:
            st.warning(t("sidebar.warning_no_collection_selected"))
            return
        
        if not embeddings_model:
            st.error(t("errors.api_key_or_embeddings_not_configured_short"))
            return

        vs, nomes_arqs = collection_manager.carregar_colecao(
            colecao_selecionada, embeddings_model
        )
        if vs and nomes_arqs:
            reset_analysis_data()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = nomes_arqs
            st.session_state.colecao_ativa = colecao_selecionada
            st.session_state.arquivos_pdf_originais = None
            st.session_state.messages = []
            st.rerun()

def handle_save_collection_section(t):
    """Lida com a secção para salvar a coleção atual."""
    st.sidebar.markdown("---")
    st.sidebar.subheader(t("sidebar.save_collection_subheader"))
    nome_nova_colecao = st.sidebar.text_input(
        t("sidebar.new_collection_name_label"),
        key="input_nome_colecao"
    )
    if st.sidebar.button(t("sidebar.save_collection_button"), key="btn_save_colecao", use_container_width=True):
        if nome_nova_colecao and st.session_state.get("nomes_arquivos"):
            collection_manager.salvar_colecao_atual(
                nome_nova_colecao,
                st.session_state.vector_store,
                st.session_state.nomes_arquivos,
                t
            )
        else:
            st.sidebar.warning(t("sidebar.warning_give_name_to_collection"))

# CORREÇÃO: Adiciona os argumentos que faltavam à assinatura da função
def display_sidebar(api_key, embeddings_model, t):
    """Renderiza a barra lateral completa da aplicação."""
    st.sidebar.header(t("sidebar.header"))
    
    # Seção para carregar documentos
    modo_documento = st.sidebar.radio(
        t("sidebar.doc_load_mode_label"),
        (t("sidebar.doc_load_mode_upload"), t("sidebar.doc_load_mode_collection")),
        key="modo_doc_radio"
    )

    if modo_documento == t("sidebar.doc_load_mode_upload"):
        handle_upload_section(api_key, embeddings_model, t)
    else:
        handle_collection_section(embeddings_model, t)

    # Seção para salvar a coleção (só aparece se houver um upload novo)
    if st.session_state.get("vector_store") and st.session_state.get("arquivos_pdf_originais"):
        handle_save_collection_section(t)

    # Exibe a coleção ou arquivos ativos
    if st.session_state.get("colecao_ativa"):
        st.sidebar.markdown(f"**{t('sidebar.active_collection')}:** `{st.session_state.colecao_ativa}`")
    elif st.session_state.get("nomes_arquivos"):
        st.sidebar.markdown(f"**{t('sidebar.loaded_files')}:** {len(st.session_state.nomes_arquivos)}")

