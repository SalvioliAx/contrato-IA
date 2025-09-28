import streamlit as st
from src.services import collection_manager, document_processor
from src.utils import reset_analysis_data

def render_sidebar(api_key, embeddings_model, t):
    """
    Renderiza todos os componentes da barra lateral, incluindo upload de ficheiros,
    gestão de coleções. O seletor de idioma foi movido para main.py.
    """
    st.sidebar.header(t("sidebar.manage_documents_header"))

    # Input da Chave de API se não estiver configurada
    if not api_key:
        st.sidebar.warning(t("warnings.api_key_not_configured"))
        st.session_state.api_key_input = st.sidebar.text_input(
            t("sidebar.api_key_input_label"),
            type="password",
            key="api_key_input_sidebar"
        )
        if st.session_state.api_key_input:
            st.rerun() # Recarrega a aplicação para usar a nova chave
        return # Para a execução se não houver chave

    st.sidebar.markdown("---")

    # Opções de carregamento de documentos
    modo_documento = st.sidebar.radio(
        t("sidebar.doc_load_mode_label"),
        (t("sidebar.doc_load_mode_upload"), t("sidebar.doc_load_mode_collection")),
        key="modo_doc_radio"
    )

    if modo_documento == t("sidebar.doc_load_mode_upload"):
        handle_upload_section(api_key, embeddings_model, t)
    else:
        handle_collection_section(embeddings_model, t)

    # Seção para salvar a coleção (só aparece se houver documentos de um novo upload)
    if st.session_state.get("vector_store") and st.session_state.get("arquivos_pdf_originais"):
        st.sidebar.markdown("---")
        st.sidebar.subheader(t("sidebar.save_collection_header"))
        nome_nova_colecao = st.sidebar.text_input(t("sidebar.new_collection_name_label"), key="input_nome_colecao")
        if st.sidebar.button(t("sidebar.save_collection_button"), use_container_width=True):
            if nome_nova_colecao and st.session_state.nomes_arquivos:
                collection_manager.salvar_colecao_atual(
                    nome_nova_colecao, 
                    st.session_state.vector_store, 
                    st.session_state.nomes_arquivos,
                    t
                )
            else:
                st.sidebar.warning(t("warnings.collection_name_and_docs_required"))

    # Exibe a coleção ou arquivos ativos
    if st.session_state.get("colecao_ativa"):
        st.sidebar.markdown(f"**{t('sidebar.active_collection')}:** `{st.session_state.colecao_ativa}`")
    elif st.session_state.get("nomes_arquivos"):
        st.sidebar.markdown(f"**{t('sidebar.loaded_files')}:** {len(st.session_state.nomes_arquivos)}")

def handle_upload_section(api_key, embeddings_model, t):
    """Lida com a lógica da seção de upload de ficheiros."""
    arquivos_pdf_upload = st.sidebar.file_uploader(
        t("sidebar.file_uploader_label"),
        type="pdf",
        accept_multiple_files=True,
        key="uploader_sidebar"
    )
    if st.sidebar.button(t("sidebar.process_uploads_button"), use_container_width=True):
        if not arquivos_pdf_upload:
            st.sidebar.warning(t("warnings.no_files_selected"))
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
            st.success(t("success.documents_processed", count=len(nomes_arqs)))
            st.rerun()
        else:
            st.error(t("errors.document_processing_failed"))

def handle_collection_section(embeddings_model, t):
    """Lida com a lógica da seção de carregamento de coleções."""
    colecoes = collection_manager.listar_colecoes_salvas()
    if not colecoes:
        st.sidebar.info(t("info.no_saved_collections"))
        return

    colecao_selecionada = st.sidebar.selectbox(
        t("sidebar.select_collection_label"),
        colecoes,
        key="select_colecao",
        index=None,
        placeholder=t("sidebar.select_collection_placeholder")
    )
    if st.sidebar.button(t("sidebar.load_collection_button"), use_container_width=True):
        if not colecao_selecionada:
            st.sidebar.warning(t("warnings.no_collection_selected"))
            return
            
        vs, nomes_arqs = collection_manager.carregar_colecao(colecao_selecionada, embeddings_model)
        if vs and nomes_arqs:
            reset_analysis_data()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = nomes_arqs
            st.session_state.colecao_ativa = colecao_selecionada
            st.session_state.arquivos_pdf_originais = None
            st.rerun()

