import streamlit as st
from services.risks import analisar_documento_para_riscos

def render_riscos_tab(embeddings_global, google_api_key):
    st.header("⚠️ Análise de Riscos")

    uploaded = st.file_uploader("Carregar contrato (PDF)", type="pdf", key="upload_risco")
    if uploaded:
        texto = uploaded.read().decode("latin-1", errors="ignore")
        relatorio = analisar_documento_para_riscos(texto, uploaded.name, google_api_key)
        st.markdown(relatorio)
