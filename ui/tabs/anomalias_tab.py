import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global, google_api_key, texts):
    """
    Renderiza a aba de Detecção de Anomalias com textos localizados.
    """
    # CORRIGIDO: Chave alterada de "anomalies_header" para "anomalias_header"
    st.header(texts["anomalias_header"]) 
    
    # CORRIGIDO: Chave alterada de "anomalies_markdown" para "anomalias_markdown"
    st.markdown(texts["anomalias_markdown"])

    # As chaves abaixo já estavam corrigidas no passo anterior
    if "dados_extraidos" not in st.session_state or not st.session_state.dados_extraidos:
        st.info(texts["anomalias_info_run_dashboard"])
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    
    if st.button(texts["anomalias_button"], use_container_width=True):
        anomalias = detectar_anomalias_no_dataframe(df)
        
        # A chave de sucesso é anomalias_success_no_anomalies
        no_anomalies_message = texts["anomalias_success_no_anomalies"]
        
        # O resultado de detectar_anomalias_no_dataframe retorna a mensagem de sucesso no final
        if anomalias and anomalias != [no_anomalies_message] and anomalias != ["Nenhum dado para analisar."]:
            st.subheader(texts["anomalias_subheader_results"])
            for a in anomalias:
                st.markdown(f"- {a}")
        else:
            st.success(no_anomalies_message)
