import streamlit as st
import pandas as pd
import altair as alt
from services.extraction import extrair_dados_dos_contratos_dinamico
import fitz  # PyMuPDF para extrair o texto completo dos arquivos

def render_dashboard_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Dashboard, agora com extração e visualização dinâmicas.
    """
    st.header("📊 Dashboard Dinâmico")
    st.markdown("Clique no botão para que a IA analise os contratos, identifique os dados mais relevantes e gere um dashboard comparativo.")

    if "vector_store_atual" not in st.session_state:
        st.info("Carregue documentos na barra lateral para usar o dashboard.")
        return

    if st.button("🚀 Gerar Dashboard Dinâmico com IA", use_container_width=True):
        arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
        if not arquivos_carregados:
            st.warning("Esta função requer os arquivos originais. Por favor, carregue os documentos novamente na barra lateral.")
            return

        # 1. Obter o texto completo de todos os documentos para a análise inicial da IA
        textos_completos_juntos = ""
        for arquivo in arquivos_carregados:
            try:
                arquivo.seek(0)
                pdf_bytes = arquivo.read()
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    textos_completos_juntos += doc.get_text() + "\n\n---\n\n"
            except Exception as e:
                st.error(f"Erro ao ler {arquivo.name}: {e}")

        if textos_completos_juntos.strip():
            # 2. Chamar o novo serviço de extração dinâmica
            dados = extrair_dados_dos_contratos_dinamico(
                st.session_state.vector_store_atual,
                st.session_state.nomes_arquivos_atuais,
                textos_completos_juntos,
                google_api_key
            )
            if dados:
                st.session_state.dados_extraidos = dados
            else:
                st.warning("A extração dinâmica não retornou dados.")
                if "dados_extraidos" in st.session_state:
                    del st.session_state.dados_extraidos

    if "dados_extraidos" in st.session_state and st.session_state.dados_extraidos:
        df = pd.DataFrame(st.session_state.dados_extraidos)
        st.dataframe(df, use_container_width=True)

        # 3. Lógica dinâmica para visualização de gráficos
        colunas_numericas = []
        for col in df.columns:
            # Tenta converter a coluna para numérico e verifica se há pelo menos um número
            if pd.to_numeric(df[col], errors='coerce').notna().any():
                colunas_numericas.append(col)
        
        if colunas_numericas:
            st.markdown("---")
            st.subheader("Visualização de Dados")
            
            coluna_selecionada = st.selectbox(
                "Selecione uma métrica numérica para visualizar:",
                options=colunas_numericas
            )
            
            if coluna_selecionada:
                df_chart = df.copy()
                # Limpa e converte a coluna para o gráfico
                df_chart[coluna_selecionada] = pd.to_numeric(df_chart[coluna_selecionada], errors='coerce')
                
                chart = alt.Chart(df_chart).mark_bar().encode(
                    x=alt.X("arquivo_fonte", title="Arquivo de Origem", sort=None),
                    y=alt.Y(coluna_selecionada, title=coluna_selecionada.replace('_', ' ').title()),
                    tooltip=["arquivo_fonte", coluna_selecionada]
                ).properties(
                    title=f"Comparativo de {coluna_selecionada.replace('_', ' ').title()}"
                )
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Nenhuma coluna puramente numérica foi extraída para gerar gráficos.")

