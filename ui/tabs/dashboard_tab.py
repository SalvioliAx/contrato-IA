import streamlit as st
import pandas as pd
import altair as alt
from services.extraction import extrair_dados_dos_contratos

def render_dashboard_tab(google_api_key):
    st.header("📊 Dashboard")

    if "vector_store_atual" not in st.session_state:
        st.info("Carregue documentos primeiro.")
        return

    if st.button("🔎 Extrair dados dos contratos"):
        dados = extrair_dados_dos_contratos(
            st.session_state.vector_store_atual,
            st.session_state.nomes_arquivos_atuais,
            google_api_key
        )
        st.session_state.dados_extraidos = dados

    if "dados_extraidos" in st.session_state:
        df = pd.DataFrame(st.session_state.dados_extraidos)
        st.dataframe(df, use_container_width=True)

        if "valor_principal_numerico" in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x="arquivo_fonte", y="valor_principal_numerico"
            )
            st.altair_chart(chart, use_container_width=True)
