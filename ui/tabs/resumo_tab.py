import streamlit as st
from services.summarizer import gerar_resumo_executivo

def render_resumo_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Resumo Executivo, usando arquivos da sessão.
    """
    st.header("📝 Resumo Executivo")

    # MODIFICADO: Usa a lista de arquivos carregados na sessão
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    
    if not arquivos_carregados:
        st.info("Carregue um ou mais documentos na barra lateral para gerar um resumo.")
        return

    nomes_arquivos = [f.name for f in arquivos_carregados]
    # Caixa de seleção para o usuário escolher o arquivo
    arquivo_selecionado_nome = st.selectbox(
        "Escolha um contrato para resumir:", 
        options=nomes_arquivos,
        index=None,
        placeholder="Selecione um arquivo"
    )

    if arquivo_selecionado_nome:
        # Encontra o objeto do arquivo selecionado
        arquivo_obj = next((f for f in arquivos_carregados if f.name == arquivo_selecionado_nome), None)
        if arquivo_obj:
            if st.button(f"Gerar Resumo para {arquivo_selecionado_nome}", use_container_width=True):
                # Lê os bytes do arquivo para enviar ao serviço de resumo
                arquivo_obj.seek(0) # Garante a leitura desde o início
                resumo = gerar_resumo_executivo(arquivo_obj.read(), arquivo_obj.name, google_api_key)
                st.markdown(resumo)
