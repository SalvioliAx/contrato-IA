import streamlit as st
from services.summarizer import gerar_resumo_executivo

def render_resumo_tab(google_api_key):
    st.header("📝 Resumo Executivo")

    uploaded = st.file_uploader("Carregar contrato (PDF)", type="pdf", key="upload_resumo")
    if uploaded:
        resumo = gerar_resumo_executivo(uploaded.read(), uploaded.name, google_api_key)
        st.markdown(resumo)
