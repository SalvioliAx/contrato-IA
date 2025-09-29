import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global, google_api_key, texts):
    """
    Renderiza a aba de Detecção de Anomalias com textos localizados.
    """
    # A chave para o cabeçalho 'anomalies_header' está correta em locale.py
    st.header(texts["anomalies_header"]) 
    # A chave para o markdown 'anomalies_markdown' está correta em locale.py
    st.markdown(texts["anomalies_markdown"])

    if "dados_extraidos" not in st.session_state or not st.session_state.dados_extraidos:
        # CORRIGIDO: Chave alterada de "anomalies_info_run_dashboard" para "anomalias_info_run_dashboard"
        st.info(texts["anomalias_info_run_dashboard"])
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    
    # A chave para o botão 'anomalias_button' está correta em locale.py
    if st.button(texts["anomalias_button"], use_container_width=True):
        anomalias = detectar_anomalias_no_dataframe(df)
        if anomalias and anomalias != [texts["anomalias_success_no_anomalies"]]:
            # A chave para o subcabeçalho 'anomalias_subheader_results' está correta em locale.py
            st.subheader(texts["anomalias_subheader_results"])
            for a in anomalias:
                st.markdown(f"- {a}")
        else:
            # CORRIGIDO: Chave alterada de "anomalias_success_no_anomalias" para "anomalias_success_no_anomalies"
            st.success(texts["anomalias_success_no_anomalies"])
