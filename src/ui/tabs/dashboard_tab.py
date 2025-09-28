import streamlit as st
import pandas as pd
from src.services import analysis

def render(t):
    """Renderiza a aba de Dashboard Comparativo."""
    st.header(t("dashboard.header"))
    st.markdown(t("dashboard.description"))

    vector_store = st.session_state.get("vector_store")
    nomes_arquivos = st.session_state.get("nomes_arquivos")

    if not vector_store or not nomes_arquivos:
        st.warning(t("warnings.load_docs_for_dashboard"))
        return

    if st.button(t("dashboard.generate_button"), use_container_width=True, key="btn_dashboard_e_anomalias"):
        dados_extraidos = analysis.extrair_dados_dos_contratos(vector_store, nomes_arquivos, t)
        if dados_extraidos:
            st.session_state.df_dashboard = pd.DataFrame(dados_extraidos)
            st.success(t("success.data_extracted_for_contracts", count=len(st.session_state.df_dashboard)))
        else:
            st.session_state.df_dashboard = pd.DataFrame()
            st.warning(t("warnings.no_data_extracted"))
        
        # Limpa as anomalias antigas ao gerar novos dados
        st.session_state.pop('anomalias_resultados', None)
        st.rerun()

    if 'df_dashboard' in st.session_state and st.session_state.df_dashboard is not None:
        if not st.session_state.df_dashboard.empty:
            st.info(t("info.extracted_data_table"))
            st.dataframe(st.session_state.df_dashboard, use_container_width=True)
        # O aviso para dataframe vazio já é tratado acima na lógica de extração
