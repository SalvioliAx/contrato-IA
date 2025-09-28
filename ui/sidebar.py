import streamlit as st
from core.processing import (
    list_saved_collections,
    save_current_collection,
    load_collection,
    create_vector_store_from_uploads
)

def _reset_session_state():
    """Limpa o estado da sessão relacionado a análises e dados antigos."""
    keys_to_clear = [
        'df_dashboard', 'resumo_gerado', 'arquivo_resumido',
        'analise_riscos_resultados', 'eventos_contratuais_df',
        'conformidade_resultados', 'anomalias_resultados', 'messages'
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = []


def render_sidebar():
    """Renderiza a barra lateral e gerencia a lógica de upload e carregamento de coleções."""
    st.sidebar.header("Gerenciar Documentos")

    mode = st.sidebar.radio(
        "Como carregar os documentos?",
        ("Fazer novo upload de PDFs", "Carregar coleção existente"),
        key="doc_mode_radio"
    )

    if mode == "Fazer novo upload de PDFs":
        handle_new_uploads()
    else:
        handle_load_collection()

    # Opção para salvar a coleção atual, se aplicável
    if st.session_state.get("vector_store") and st.session_state.get("arquivos_pdf_originais"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Salvar Coleção Atual")
        new_collection_name = st.sidebar.text_input("Nome para a nova coleção:", key="input_new_collection")
        if st.sidebar.button("Salvar Coleção", use_container_width=True):
            if new_collection_name and st.session_state.get("nomes_arquivos"):
                save_current_collection(
                    new_collection_name,
                    st.session_state.vector_store,
                    st.session_state.nomes_arquivos
                )
            else:
                st.sidebar.warning("Dê um nome e certifique-se de que há documentos carregados.")

    # Exibe o status atual
    if st.session_state.get("colecao_ativa"):
        st.sidebar.markdown(f"**Coleção Ativa:** `{st.session_state.colecao_ativa}`")
    elif st.session_state.get("nomes_arquivos"):
        st.sidebar.markdown(f"**Arquivos Carregados:** {len(st.session_state.nomes_arquivos)}")

def handle_new_uploads():
    """Lida com a interface e lógica para o upload de novos arquivos PDF."""
    uploaded_files = st.sidebar.file_uploader(
        "Selecione um ou mais contratos em PDF",
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    if st.sidebar.button("Processar Documentos Carregados", use_container_width=True):
        if not uploaded_files:
            st.sidebar.warning("Por favor, selecione pelo menos um arquivo PDF.")
            return
        if not st.session_state.get("google_api_key") or not st.session_state.get("embeddings_model"):
            st.sidebar.error("Chave de API ou Embeddings não configurados corretamente.")
            return

        vs, names = create_vector_store_from_uploads(uploaded_files, st.session_state.embeddings_model)

        if vs and names:
            _reset_session_state()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = names
            st.session_state.arquivos_pdf_originais = uploaded_files
            st.session_state.colecao_ativa = None
            st.success(f"{len(names)} Documento(s) processado(s)!")
            st.rerun()
        else:
            st.error("Falha ao processar documentos. Verifique os logs acima.")

def handle_load_collection():
    """Lida com a interface e lógica para carregar uma coleção existente."""
    collections = list_saved_collections()
    if not collections:
        st.sidebar.info("Nenhuma coleção salva ainda.")
        return

    selected_collection = st.sidebar.selectbox(
        "Escolha uma coleção:",
        collections,
        index=None,
        placeholder="Selecione uma coleção"
    )
    if st.sidebar.button("Carregar Coleção Selecionada", use_container_width=True):
        if not selected_collection:
            st.sidebar.warning("Por favor, escolha uma coleção.")
            return
        if not st.session_state.get("google_api_key") or not st.session_state.get("embeddings_model"):
            st.sidebar.error("Chave de API ou Embeddings não configurados.")
            return

        vs, names = load_collection(selected_collection, st.session_state.embeddings_model)
        if vs and names:
            _reset_session_state()
            st.session_state.vector_store = vs
            st.session_state.nomes_arquivos = names
            st.session_state.colecao_ativa = selected_collection
            st.session_state.arquivos_pdf_originais = None
            st.rerun()
