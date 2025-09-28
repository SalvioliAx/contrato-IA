import streamlit as st
import pandas as pd
import altair as alt
from services.extraction import extrair_dados_dos_contratos

def render_dashboard_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Dashboard para extração e visualização de dados.
    """
    st.header("📊 Dashboard de Extração de Dados")

    if "vector_store_atual" not in st.session_state:
        st.info("Carregue documentos na barra lateral para usar o dashboard.")
        return

    if st.button("🔎 Extrair dados dos contratos para Dashboard e Anomalias", use_container_width=True):
        dados = extrair_dados_dos_contratos(
            st.session_state.vector_store_atual,
            st.session_state.nomes_arquivos_atuais,
            google_api_key
        )
        if dados:
            st.session_state.dados_extraidos = dados
        else:
            st.warning("A extração não retornou dados.")

    if "dados_extraidos" in st.session_state and st.session_state.dados_extraidos:
        df = pd.DataFrame(st.session_state.dados_extraidos)
        st.dataframe(df, use_container_width=True)

        # Gráfico de exemplo: Valor Principal por Contrato
        if "valor_principal_numerico" in df.columns:
            # Garante que a coluna seja numérica para o gráfico
            df_chart = df.copy()
            df_chart["valor_principal_numerico"] = pd.to_numeric(df_chart["valor_principal_numerico"], errors='coerce')
            
            chart = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X("arquivo_fonte", title="Arquivo de Origem"), 
                y=alt.Y("valor_principal_numerico", title="Valor Principal"),
                tooltip=["arquivo_fonte", "valor_principal_numerico"]
            ).properties(
                title="Comparativo de Valor Principal por Contrato"
            )
            st.altair_chart(chart, use_container_width=True)
