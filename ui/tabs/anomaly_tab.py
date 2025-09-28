import streamlit as st
from core.analysis import detectar_anomalias_no_dataframe

def render():
    st.header("📊 Detecção de Anomalias Contratuais")
    st.markdown(
        "Identifica dados que fogem do padrão no conjunto de contratos carregados. "
        "**Nota:** Esta funcionalidade depende da qualidade e consistência da extração de dados realizada na aba '📈 Dashboard'."
    )

    df_for_anomalies = st.session_state.get("df_dashboard")

    if df_for_anomalies is None or df_for_anomalies.empty:
        st.warning(
            "Os dados para análise de anomalias ainda não foram gerados. "
            "Por favor, vá para a aba '📈 Dashboard' e clique em "
            "'🚀 Gerar Dados para Dashboard' primeiro."
        )
        return

    st.info("Analisando os dados extraídos da aba 'Dashboard' em busca de anomalias.")
    if st.button("🚨 Detectar Anomalias Agora", key="btn_detect_anomalies", use_container_width=True):
        with st.spinner("Detectando anomalias..."):
            st.session_state.anomalias_resultados = detectar_anomalias_no_dataframe(df_for_anomalies.copy())
        st.rerun()

    if "anomalias_resultados" in st.session_state:
        st.subheader("Resultados da Detecção de Anomalias:")
        results = st.session_state.anomalias_resultados
        if isinstance(results, list) and results:
            for item in results:
                st.markdown(f"- {item}")
        else:
            st.info("Nenhuma anomalia significativa detectada com os critérios atuais.")
