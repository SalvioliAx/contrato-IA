import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global=None, google_api_key=None):
    st.header("🔎 Detecção de Anomalias")

    if "dados_extraidos" not in st.session_state:
        st.info("Extraia dados primeiro no Dashboard.")
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    anomalias = detectar_anomalias_no_dataframe(df)
    for a in anomalias:
        st.markdown(f"- {a}")
