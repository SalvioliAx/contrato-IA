import streamlit as st
from src.services import analysis

def render(t):
    """Renderiza a aba de Detecção de Anomalias."""
    st.header(t("anomalies.header"))
    st.markdown(t("anomalies.description"))

    df_para_anomalias = st.session_state.get("df_dashboard")

    if df_para_anomalias is None or df_para_anomalias.empty:
        st.warning(t("warnings.generate_dashboard_data_first"))
        return

    st.info(t("info.analyzing_dashboard_data"))
    if st.button(t("anomalies.detect_button"), use_container_width=True, key="btn_detectar_anomalias"):
        st.session_state.anomalias_resultados = analysis.detectar_anomalias_no_dataframe(
            df_para_anomalias.copy(), t
        )
        st.rerun()

    if "anomalias_resultados" in st.session_state and st.session_state.anomalias_resultados:
        st.subheader(t("anomalies.results_header"))
        resultados = st.session_state.anomalias_resultados
        if isinstance(resultados, list) and len(resultados) > 0:
            for item in resultados:
                st.markdown(f"- {item}")
        else:
            st.info(t("anomalies.no_significant_anomalies"))
