import streamlit as st
import pandas as pd
import altair as alt
from services.extraction import extrair_dados_dos_contratos_dinamico
import fitz

def render_dashboard_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Renderiza a aba de Dashboard, com fluxo de execução corrigido para exibir mensagens.
    """
    st.header(texts["dashboard_header"])
    st.markdown(texts["dashboard_markdown"])

    if "vector_store_atual" not in st.session_state:
        st.info(texts["dashboard_info_load_docs"])
        return

    if st.button(texts["dashboard_button_generate"], use_container_width=True):
        arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
        if not arquivos_carregados:
            st.warning(texts["dashboard_warning_no_files"])
            return

        with st.spinner(texts["dashboard_spinner_generating"]):
            textos_completos_juntos = ""
            for arquivo in arquivos_carregados:
                try:
                    arquivo.seek(0)
                    pdf_bytes = arquivo.read()
                    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                        for page in doc:
                            textos_completos_juntos += page.get_text() + "\n"
                        textos_completos_juntos += "\n\n---\n\n"
                except Exception as e:
                    st.error(texts["dashboard_error_read_file"].format(filename=arquivo.name, error=e))
            
            if textos_completos_juntos.strip():
                dados = extrair_dados_dos_contratos_dinamico(
                    st.session_state.vector_store_atual,
                    st.session_state.nomes_arquivos_atuais,
                    textos_completos_juntos,
                    google_api_key,
                    lang_code
                )
                if dados:
                    st.session_state.dados_extraidos = dados
                    # CORREÇÃO: Mover o st.rerun() para DENTRO do if de sucesso
                    st.rerun()
                else:
                    st.warning(texts["dashboard_warning_no_data"])
                    if "dados_extraidos" in st.session_state:
                        del st.session_state.dados_extraidos
            # CORREÇÃO: Remover o st.rerun() que estava aqui fora

    if "dados_extraidos" in st.session_state and st.session_state.dados_extraidos:
        df = pd.DataFrame(st.session_state.dados_extraidos)
        st.dataframe(df, use_container_width=True)

        # A lógica para detectar colunas numéricas foi levemente ajustada para ser mais robusta
        colunas_numericas = []
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(pd.to_numeric(df[col], errors='coerce')):
                 # Garante que a coluna não seja inteira de NaNs
                if pd.to_numeric(df[col], errors='coerce').notna().any():
                    colunas_numericas.append(col)
        
        if colunas_numericas:
            st.markdown("---")
            st.subheader(texts["dashboard_subheader_viz"])
            
            coluna_selecionada = st.selectbox(texts["dashboard_selectbox_metric"], options=colunas_numericas)
            
            if coluna_selecionada:
                df_chart = df.copy()
                df_chart[coluna_selecionada] = pd.to_numeric(df_chart[coluna_selecionada], errors='coerce')
                
                chart = alt.Chart(df_chart).mark_bar().encode(
                    x=alt.X("arquivo_fonte", title=texts["dashboard_chart_axis_x"], sort=None),
                    y=alt.Y(coluna_selecionada, title=coluna_selecionada.replace('_', ' ').title()),
                    tooltip=["arquivo_fonte", coluna_selecionada]
                ).properties(title=texts["dashboard_chart_title"].format(column=coluna_selecionada.replace('_', ' ').title()))
                st.altair_chart(chart, use_container_width=True)
        else:
            st.info(texts["dashboard_info_no_numeric"])

