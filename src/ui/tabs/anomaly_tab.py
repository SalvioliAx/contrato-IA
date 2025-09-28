import streamlit as st
from src.services import analysis

def display_anomaly_tab(t):
    """Renderiza a aba de Detecção de Anomalias."""
    st.header(t("anomalies.header"))
    st.markdown(t("anomalies.description"))

    df_para_anomalias = st.session_state.get("df_dashboard")

    if df_para_anomalias is None or df_para_anomalias.empty:
        st.warning(t("warnings.generate_dashboard_data_first"))
        return

    st.info(t("info.analyzing_dashboard_data"))
    if st.button(t("anomalies.detect_anomalies_button"), key="btn_anomaly_detect", use_container_width=True):
        st.session_state.anomalias_resultados = analysis.detectar_anomalias_no_dataframe(df_para_anomalias.copy(), t)
        st.rerun()

    if "anomalias_resultados" in st.session_state:
        st.subheader(t("anomalies.results_subheader"))
        resultados = st.session_state.anomalias_resultados
        if resultados:
            for item in resultados:
                st.markdown(f"- {item}")
        else:
            st.info(t("info.no_anomalies_found"))

