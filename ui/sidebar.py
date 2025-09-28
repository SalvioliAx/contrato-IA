import streamlit as st
from services.collections import (
    listar_colecoes_salvas, salvar_colecao_atual, carregar_colecao
)
from services.document_loader import obter_vector_store_de_uploads

def render_sidebar(embeddings_global, google_api_key):
    """
    Renderiza a barra lateral para upload de arquivos e gerenciamento de coleções.
    """
    st.sidebar.header("📂 Gerenciador de Documentos")

    # Widget para upload de múltiplos arquivos PDF
    uploaded_files = st.sidebar.file_uploader(
        "Carregar novos contratos (PDF)", type=["pdf"], accept_multiple_files=True, key="upload_pdf"
    )

    # Lógica para salvar a sessão atual como uma coleção
    nome_colecao_salvar = st.sidebar.text_input("Nome para salvar a coleção atual:")
    if st.sidebar.button("💾 Salvar coleção"):
        if "vector_store_atual" in st.session_state and uploaded_files: # Só permite salvar se veio de um upload
            salvar_colecao_atual(
                nome_colecao_salvar,
                st.session_state.vector_store_atual,
                st.session_state.nomes_arquivos_atuais
            )
        else:
            st.sidebar.warning("Carregue novos arquivos para poder salvar uma coleção.")


    st.sidebar.markdown("---")
    # Lógica para carregar uma coleção existente
    colecoes_existentes = listar_colecoes_salvas()
    if colecoes_existentes:
        colecao_selecionada = st.sidebar.selectbox("Ou abrir uma coleção salva:", colecoes_existentes, index=None, placeholder="Selecione uma coleção")
        if st.sidebar.button("📂 Carregar coleção"):
            if colecao_selecionada and embeddings_global:
                vs, nomes = carregar_colecao(colecao_selecionada, embeddings_global)
                if vs:
                    # Atualiza o estado da sessão com a coleção carregada
                    st.session_state.vector_store_atual = vs
                    st.session_state.nomes_arquivos_atuais = nomes
                    # ADICIONADO: Limpa os arquivos originais ao carregar uma coleção
                    st.session_state.arquivos_pdf_originais = None 
                    st.session_state.messages = [] # Limpa o chat
                    st.rerun()
            else:
                st.sidebar.error("Selecione uma coleção e certifique-se que a API Key está configurada.")

    # Processa os arquivos recém-carregados
    if uploaded_files:
        # Botão para iniciar o processamento, evitando reprocessamento a cada interação
        if st.sidebar.button("Processar Documentos Carregados"):
            vs, nomes = obter_vector_store_de_uploads(uploaded_files, embeddings_global, google_api_key)
            if vs:
                st.session_state.vector_store_atual = vs
                st.session_state.nomes_arquivos_atuais = nomes
                # ADICIONADO: Salva os objetos de arquivo originais na sessão
                st.session_state.arquivos_pdf_originais = uploaded_files
                st.session_state.messages = [] # Limpa o chat
                st.rerun() # Recarrega a página para refletir o novo estado
