import streamlit as st
from src.services import analysis

def render(api_key, t):
    """Renderiza a aba de Resumo Executivo."""
    st.header(t("summary.header"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.warning(t("warnings.upload_docs_for_summary"))
        return

    nomes_arquivos = [f.name for f in arquivos_originais]
    arquivo_selecionado = st.selectbox(
        t("summary.select_contract_label"),
        options=nomes_arquivos,
        index=None,
        placeholder=t("summary.select_file_placeholder"),
        key="select_resumo_tab"
    )

    if st.button(t("summary.generate_button"), use_container_width=True, key="btn_resumo_tab"):
        if not arquivo_selecionado:
            st.warning(t("warnings.no_file_selected_for_summary"))
            return
            
        arquivo_obj = next((arq for arq in arquivos_originais if arq.name == arquivo_selecionado), None)
        if arquivo_obj:
            resumo = analysis.gerar_resumo_executivo(arquivo_obj, api_key, t)
            st.session_state.resumo_gerado = resumo
            st.session_state.arquivo_resumido = arquivo_selecionado
            st.rerun()
        else:
            st.error(t("errors.file_not_found_internal"))

    # Exibe o resumo se ele corresponder ao arquivo selecionado
    if st.session_state.get("arquivo_resumido") == arquivo_selecionado and st.session_state.get("resumo_gerado"):
        st.subheader(t("summary.summary_of_contract", file=st.session_state.arquivo_resumido))
        st.markdown(st.session_state.resumo_gerado)
