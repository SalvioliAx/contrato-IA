import streamlit as st
import pandas as pd
from src.services import analysis

def display_dashboard_tab(t):
    """Renderiza a aba de Dashboard Comparativo."""
    st.header(t("dashboard.header"))
    st.markdown(t("dashboard.description"))

    vector_store = st.session_state.get("vector_store")
    nomes_arquivos = st.session_state.get("nomes_arquivos")

    if not (vector_store and nomes_arquivos):
        st.warning(t("warnings.load_docs_for_dashboard"))
        return

    if st.button(t("dashboard.generate_data_button"), key="btn_dashboard_generate", use_container_width=True):
        dados_extraidos = analysis.extrair_dados_dos_contratos(vector_store, nomes_arquivos, t)
        if dados_extraidos:
            st.session_state.df_dashboard = pd.DataFrame(dados_extraidos)
            st.success(t("success.data_extracted_for_dashboard", count=len(st.session_state.df_dashboard)))
        else:
            st.session_state.df_dashboard = pd.DataFrame()
            st.warning(t("warnings.no_data_extracted"))
        
        # Limpa as anomalias antigas para forçar um recálculo
        if 'anomalias_resultados' in st.session_state:
            del st.session_state['anomalias_resultados']
        st.rerun()

    if 'df_dashboard' in st.session_state and not st.session_state.df_dashboard.empty:
        st.info(t("dashboard.data_table_info"))
        st.dataframe(st.session_state.df_dashboard, use_container_width=True)

