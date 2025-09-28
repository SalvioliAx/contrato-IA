import streamlit as st
from services.collections import (
    listar_colecoes_salvas, salvar_colecao_atual, carregar_colecao
)
from services.document_loader import obter_vector_store_de_uploads

def render_sidebar(embeddings_global, google_api_key):
    st.sidebar.header("📂 Documentos")

    uploaded_files = st.sidebar.file_uploader(
        "Carregar PDF(s)", type=["pdf"], accept_multiple_files=True, key="upload_pdf"
    )

    colecao_salvar = st.sidebar.text_input("Nome da coleção para salvar:")
    if st.sidebar.button("💾 Salvar coleção atual"):
        if "vector_store_atual" in st.session_state:
            salvar_colecao_atual(
                colecao_salvar,
                st.session_state.vector_store_atual,
                st.session_state.nomes_arquivos_atuais
            )

    colecoes_existentes = listar_colecoes_salvas()
    colecao_selecionada = st.sidebar.selectbox("Abrir coleção salva:", colecoes_existentes)
    if st.sidebar.button("📂 Carregar coleção selecionada"):
        vs, nomes = carregar_colecao(colecao_selecionada, embeddings_global)
        if vs:
            st.session_state.vector_store_atual = vs
            st.session_state.nomes_arquivos_atuais = nomes

    # Upload inicial → cria vector store
    if uploaded_files:
        vs, nomes = obter_vector_store_de_uploads(uploaded_files, embeddings_global, google_api_key)
        if vs:
            st.session_state.vector_store_atual = vs
            st.session_state.nomes_arquivos_atuais = nomes
