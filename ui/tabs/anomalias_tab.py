import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global, google_api_key, texts):
    """
    Renderiza a aba de Detecção de Anomalias com textos localizados.
    """
    st.header(texts["anomalies_header"])
    st.markdown(texts["anomalies_markdown"])

    if "dados_extraidos" not in st.session_state or not st.session_state.dados_extraidos:
        st.info(texts["anomalies_info_run_dashboard"])
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    
    if st.button(texts["anomalies_button"], use_container_width=True):
        anomalias = detectar_anomalias_no_dataframe(df)
        if anomalias:
            st.subheader(texts["anomalies_subheader_results"])
            for a in anomalias:
                st.markdown(f"- {a}")
        else:
            st.success(texts["anomalies_success_no_anomalies"])

