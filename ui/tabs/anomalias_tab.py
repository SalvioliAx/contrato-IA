import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global, google_api_key, texts):
    """
    Renderiza a aba de Detecção de Anomalias com textos localizados.
    """
    # CORRIGIDO: Chave alterada para "anomalies_header", pois é a chave que existe no dicionário 'en' e 'es'.
    st.header(texts["anomalies_header"]) 
    
    # CORRIGIDO: Chave alterada para "anomalies_markdown", pois é a chave que existe no dicionário 'en' e 'es'.
    st.markdown(texts["anomalies_markdown"])

    # As chaves abaixo TAMBÉM PRECISAM SER PADRONIZADAS:
    if "dados_extraidos" not in st.session_state or not st.session_state.dados_extraidos:
        # CORRIGIDO: Chave alterada para "anomalies_info_run_dashboard"
        st.info(texts["anomalies_info_run_dashboard"])
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    
    # CORRIGIDO: Chave alterada para "anomalies_button"
    if st.button(texts["anomalies_button"], use_container_width=True):
        anomalias = detectar_anomalias_no_dataframe(df)
        
        # CORRIGIDO: Chave alterada para "anomalies_success_no_anomalies"
        no_anomalies_message = texts["anomalies_success_no_anomalies"]
        
        # CORRIGIDO: Chave alterada para "anomalies_subheader_results"
        if anomalias and anomalias != [no_anomalies_message] and anomalias != ["Nenhum dado para analisar."]:
            st.subheader(texts["anomalies_subheader_results"])
            for a in anomalias:
                st.markdown(f"- {a}")
        else:
            st.success(no_anomalies_message)
