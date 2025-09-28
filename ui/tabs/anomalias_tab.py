import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global=None, google_api_key=None):
    """
    Renderiza a aba de Detecção de Anomalias.
    """
    st.header("🔎 Detecção de Anomalias")
    st.markdown("Esta aba analisa os dados extraídos do dashboard para encontrar valores que fogem do padrão (outliers).")

    # Verifica se os dados já foram extraídos na aba do dashboard
    if "dados_extraidos" not in st.session_state or not st.session_state.dados_extraidos:
        st.info("Para começar, vá para a aba 'Dashboard' e clique em 'Extrair dados dos contratos'.")
        return

    df = pd.DataFrame(st.session_state.dados_extraidos)
    
    if st.button("Detectar Anomalias nos Dados", use_container_width=True):
        anomalias = detectar_anomalias_no_dataframe(df)
        if anomalias:
            st.subheader("Resultados da Análise:")
            for a in anomalias:
                st.markdown(f"- {a}")
        else:
            st.success("Nenhuma anomalia significativa foi encontrada.")
