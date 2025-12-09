import streamlit as st
import pandas as pd
import altair as alt
import fitz
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from services.extraction import extrair_dados_dos_contratos_dinamico

def render_dashboard_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Dashboard Streamlit para análise de contratos usando LangChain 2025.
    Mantém toda a lógica de extração e visualização do histórico.
    """
    st.header(texts["dashboard_header"])
    st.markdown(texts["dashboard_markdown"])

    # Verifica se o vetor store está carregado
    if "vector_store_atual" not in st.session_state:
        st.info(texts["dashboard_info_load_docs"])
        return

    # Botão para processar arquivos
    if st.button(texts["dashboard_button_generate"], use_container_width=True):
        arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
        if not arquivos_carregados or len(arquivos_carregados) < 1:
            st.warning(texts["dashboard_warning_no_files"])
            return

        with st.spinner(texts["dashboard_spinner_generating"]):
            textos_completos_juntos = ""
            nomes_arquivos = []

            for arquivo in arquivos_carregados:
                try:
                    arquivo.seek(0)
                    pdf_bytes = arquivo.read()
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                        for page in doc:
                            textos_completos_juntos += page.get_text() + "\n"
                        textos_completos_juntos += "\n\n---\n\n"
                        nomes_arquivos.append(arquivo.name)
                except Exception as e:
                    st.error(texts["dashboard_error_read_file"].format(filename=arquivo.name, error=e))

            # Extrai dados se houver texto
            if textos_completos_juntos.strip():
                dados = extrair_dados_dos_contratos_dinamico(
                    st.session_state.vector_store_atual,
                    nomes_arquivos,
                    textos_completos_juntos,
                    google_api_key,
                    lang_code
                )

                if dados:
                    st.session_state.dados_extraidos = dados
                    st.rerun()  # só faz rerun se dados foram extraídos
                else:
                    st.warning(texts["dashboard_warning_no_data"])
                    st.session_state.pop("dados_extraidos", None)

    # Exibe tabela e gráficos se houver dados
    if "dados_extraidos" in st.session_state and st.session_state.dados_extraidos:
        df = pd.DataFrame(st.session_state.dados_extraidos)
        st.dataframe(df, use_container_width=True)

        # Detecta colunas numéricas
        colunas_numericas = [
            col for col in df.columns
            if pd.to_numeric(df[col], errors='coerce').notna().any()
        ]

        if colunas_numericas:
            st.markdown("---")
            st.subheader(texts["dashboard_subheader_viz"])
            coluna_selecionada = st.selectbox(
                texts["dashboard_selectbox_metric"], options=colunas_numericas
            )

            if coluna_selecionada:
                df_chart = df.copy()
                df_chart[coluna_selecionada] = pd.to_numeric(df_chart[coluna_selecionada], errors='coerce')

                chart = alt.Chart(df_chart).mark_bar().encode(
                    x=alt.X(
                        "arquivo_fonte",
                        sort=None,
                        title=texts["dashboard_chart_axis_x"]
                    ),
                    y=alt.Y(
                        coluna_selecionada,
                        title=coluna_selecionada.replace('_', ' ').title()
                    ),
                    tooltip=["arquivo_fonte", coluna_selecionada]
                ).properties(
                    title=texts["dashboard_chart_title"].format(column=coluna_selecionada.replace('_', ' ').title())
                )
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info(texts["dashboard_info_no_numeric"])
