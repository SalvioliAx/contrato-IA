import streamlit as st
from services.risks import analisar_documento_para_riscos
import fitz # PyMuPDF para extrair o texto

def render_riscos_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Análise de Riscos, usando arquivos da sessão.
    """
    st.header("⚠️ Análise de Riscos")

    # MODIFICADO: Usa a lista de arquivos carregados na sessão
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    
    if not arquivos_carregados:
        st.info("Carregue um ou mais documentos na barra lateral para analisar os riscos.")
        return

    nomes_arquivos = [f.name for f in arquivos_carregados]
    arquivo_selecionado_nome = st.selectbox(
        "Escolha um contrato para analisar os riscos:", 
        options=nomes_arquivos,
        index=None,
        placeholder="Selecione um arquivo"
    )
    
    if arquivo_selecionado_nome:
        arquivo_obj = next((f for f in arquivos_carregados if f.name == arquivo_selecionado_nome), None)
        if arquivo_obj:
            if st.button(f"Analisar Riscos em {arquivo_selecionado_nome}", use_container_width=True):
                # Extrai o texto completo do PDF antes de enviar para análise
                texto_completo = ""
                try:
                    arquivo_obj.seek(0)
                    pdf_bytes = arquivo_obj.read()
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                        for page in doc:
                            texto_completo += page.get_text() + "\n"
                except Exception as e:
                    st.error(f"Erro ao extrair texto do PDF: {e}")
                    return # Para a execução se não conseguir ler

                if texto_completo.strip():
                    relatorio = analisar_documento_para_riscos(texto_completo, arquivo_obj.name, google_api_key)
                    st.markdown(relatorio)
                else:
                    st.warning("Não foi possível extrair conteúdo de texto do documento para análise.")
