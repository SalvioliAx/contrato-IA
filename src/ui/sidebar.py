import streamlit as st
from src.services import collection_manager, document_processor
from src.utils import reset_analysis_data

def _handle_upload_section(t):
    """Lida com a lógica de upload de novos ficheiros PDF."""
    arquivos_pdf_upload = st.sidebar.file_uploader(
        t("sidebar.file_uploader_label"),
        type="pdf",
        accept_multiple_files=True
    )
    
    if st.sidebar.button(t("sidebar.process_uploads_button")):
        if not st.session_state.get("embeddings_model"):
            st.sidebar.error(t("errors.api_key_or_embeddings_not_configured"))
            return
        if not arquivos_pdf_upload:
            st.sidebar.warning(t("warnings.no_files_selected"))
            return
        
        with st.spinner(t("info.processing_and_indexing")):
            vs, nomes_arqs = document_processor.obter_vector_store_de_uploads(
                arquivos_pdf_upload, 
                st.session_state.embeddings_model, 
                t
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

def _handle_collection_section(t):
    """Lida com a lógica de carregamento de uma coleção existente."""
    colecoes_disponiveis = collection_manager.listar_colecoes_salvas()
    if colecoes_disponiveis:
        colecao_selecionada = st.sidebar.selectbox(
            t("sidebar.select_collection_label"),
            colecoes_disponiveis,
            index=None,
            placeholder=t("sidebar.select_collection_placeholder")
        )
        if st.sidebar.button(t("sidebar.load_collection_button")):
            if not colecao_selecionada:
                st.sidebar.warning(t("warnings.no_collection_selected"))
                return
            if not st.session_state.get("embeddings_model"):
                st.sidebar.error(t("errors.api_key_or_embeddings_not_configured"))
                return

            vs, nomes_arqs = collection_manager.carregar_colecao(
                colecao_selecionada, 
                st.session_state.embeddings_model,
                t
            )
            if vs and nomes_arqs:
                reset_analysis_data()
                st.session_state.vector_store = vs
                st.session_state.nomes_arquivos = nomes_arqs
                st.session_state.colecao_ativa = colecao_selecionada
                st.session_state.arquivos_pdf_originais = None
                st.rerun()
    else:
        st.sidebar.info(t("info.no_saved_collections"))

def display_sidebar(t):
    """Renderiza toda a barra lateral."""
    with st.sidebar:
        st.header(t("sidebar.manage_documents_header"))

        # Adiciona a opção de inserir a chave de API se não for encontrada
        if not st.secrets.get("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            st.session_state.api_key_input = st.text_input(
                t("sidebar.api_key_input_label"),
                type="password",
                key="api_key_sidebar_input"
            )

        modo_documento = st.radio(
            t("sidebar.doc_load_mode_label"),
            (t("sidebar.doc_load_mode_upload"), t("sidebar.doc_load_mode_collection")),
            key="modo_doc_radio"
        )

        if modo_documento == t("sidebar.doc_load_mode_upload"):
            _handle_upload_section(t)
        else:
            _handle_collection_section(t)

        # Seção para salvar a coleção
        if st.session_state.get("vector_store") and st.session_state.get("arquivos_pdf_originais"):
            st.markdown("---")
            st.subheader(t("sidebar.save_collection_header"))
            nome_nova_colecao = st.text_input(t("sidebar.new_collection_name_label"))
            if st.button(t("sidebar.save_collection_button")):
                if nome_nova_colecao and st.session_state.nomes_arquivos:
                    collection_manager.salvar_colecao_atual(
                        nome_nova_colecao,
                        st.session_state.vector_store,
                        st.session_state.nomes_arquivos,
                        t
                    )
                else:
                    st.warning(t("warnings.collection_name_and_docs_required"))
        
        # Exibe o status atual
        if st.session_state.get("colecao_ativa"):
            st.markdown(f"**{t('sidebar.active_collection')}:** `{st.session_state.colecao_ativa}`")
        elif st.session_state.get("nomes_arquivos"):
            st.markdown(f"**{t('sidebar.loaded_files')}:** {len(st.session_state.nomes_arquivos)}")

