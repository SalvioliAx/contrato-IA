import streamlit as st
from services.events import extrair_eventos_dos_contratos

def render_prazos_tab(embeddings_global, google_api_key):
    st.header("⏳ Prazos e Eventos")

    if "dados_extraidos" not in st.session_state:
        st.info("Extraia dados primeiro no Dashboard.")
        return

    eventos = extrair_eventos_dos_contratos(
        [{"nome": d["arquivo_fonte"], "texto": str(d)} for d in st.session_state.dados_extraidos],
        google_api_key
    )
    if eventos:
        st.table(eventos)
