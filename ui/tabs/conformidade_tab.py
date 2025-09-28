import streamlit as st
from services.compliance import verificar_conformidade_documento

def render_conformidade_tab(google_api_key):
    st.header("✅ Verificação de Conformidade")

    ref = st.file_uploader("Carregar documento de referência (PDF)", type="pdf", key="ref")
    doc = st.file_uploader("Carregar documento a comparar (PDF)", type="pdf", key="doc")

    if ref and doc:
        ref_text = ref.read().decode("latin-1", errors="ignore")
        doc_text = doc.read().decode("latin-1", errors="ignore")
        relatorio = verificar_conformidade_documento(ref_text, ref.name, doc_text, doc.name, google_api_key)
        st.markdown(relatorio)
