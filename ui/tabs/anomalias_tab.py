import streamlit as st
import pandas as pd
from services.anomalies import detectar_anomalias_no_dataframe

def render_anomalias_tab(embeddings_global, google_api_key, texts):
    """
    Renderiza a aba de Detecção de Anomalias com textos localizados.
    """

    st.header(texts["anomalias_header"])
    st.markdown(texts["anomalias_markdown"])

    # ----------------------------
    # Validate extracted data
    # ----------------------------
    dados = st.session_state.get("dados_extraidos")

    if not dados or not isinstance(dados, (list, dict)):
        st.info(texts["anomalias_info_run_dashboard"])
        return

    # Evita erro caso dados venham como dict (1 registro só)
    try:
        df = pd.DataFrame(dados)
    except Exception:
        st.error("Erro ao converter os dados extraídos para DataFrame.")
        return

    # ----------------------------
    # Run anomaly detection
    # ----------------------------
    if st.button(texts["anomalias_button"], use_container_width=True):

        # Executa detecção
        try:
            anomalias = detectar_anomalias_no_dataframe(df)
        except Exception as e:
            st.error(f"Erro ao analisar anomalias: {str(e)}")
            return

        # Normaliza resultados
        if not anomalias or anomalias in ([], ["Nenhum dado para analisar."]):
            st.success(texts["anomalias_success_no_anomalies"])
            return

        # Caso o script tenha retornado apenas a mensagem de “nenhuma anomalia”
        no_ano_msg = texts["anomalias_success_no_anomalies"]
        if anomalias == [no_ano_msg]:
            st.success(no_ano_msg)
            return

        # ----------------------------
        # Show anomaly results
        # ----------------------------
        st.subheader(texts["anomalias_subheader_results"])

        for a in anomalias:
            st.markdown(f"- {a}")
