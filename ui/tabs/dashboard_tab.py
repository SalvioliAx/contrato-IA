import streamlit as st
import pandas as pd
from core.analysis import extrair_dados_dos_contratos

def render():
    st.header("📈 Análise Comparativa de Dados Contratuais")
    st.markdown("Clique no botão para extrair e comparar os dados chave dos documentos carregados.")

    vector_store = st.session_state.get("vector_store")
    file_names = st.session_state.get("nomes_arquivos")

    if not (vector_store and file_names):
        st.warning("Carregue documentos ou uma coleção válida para usar o dashboard.")
        return

    if st.button("🚀 Gerar Dados para Dashboard", key="btn_dashboard", use_container_width=True):
        extracted_data = extrair_dados_dos_contratos(vector_store, file_names)
        if extracted_data:
            st.session_state.df_dashboard = pd.DataFrame(extracted_data)
            st.success(f"Dados extraídos para {len(st.session_state.df_dashboard)} contratos.")
        else:
            st.session_state.df_dashboard = pd.DataFrame()
            st.warning("Nenhum dado foi extraído para o dashboard.")
        
        # Limpa dados de anomalias antigas para forçar nova análise
        st.session_state.pop('anomalias_resultados', None)
        st.rerun()

    if 'df_dashboard' in st.session_state and not st.session_state.df_dashboard.empty:
        st.info("Tabela de dados extraídos dos contratos.")
        st.dataframe(st.session_state.df_dashboard, use_container_width=True)
