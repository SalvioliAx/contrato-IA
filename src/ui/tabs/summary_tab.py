import streamlit as st
from src.services import analysis

def display_summary_tab(t):
    """Renderiza a aba de Resumo Executivo."""
    st.header(t("summary.header"))
    
    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.info(t("info.upload_new_docs_for_summary"))
        return

    lista_nomes = [f.name for f in arquivos_originais]
    arquivo_selecionado_nome = st.selectbox(
        t("summary.select_contract_label"),
        options=lista_nomes,
        key="select_summary_file",
        index=None,
        placeholder=t("summary.select_file_placeholder")
    )

    if arquivo_selecionado_nome and st.button(t("summary.generate_summary_button"), key="btn_summary_generate", use_container_width=True):
        arquivo_obj = next((arq for arq in arquivos_originais if arq.name == arquivo_selecionado_nome), None)
        if arquivo_obj:
            arquivo_bytes = arquivo_obj.getvalue()
            resumo = analysis.gerar_resumo_executivo(arquivo_bytes, arquivo_obj.name, t)
            st.session_state.resumo_gerado = resumo
            st.session_state.arquivo_resumido = arquivo_selecionado_nome
            st.rerun()
        else:
            st.error(t("errors.file_not_found_in_session"))
    
    if st.session_state.get("arquivo_resumido") == arquivo_selecionado_nome and st.session_state.get("resumo_gerado"):
        st.subheader(t("summary.summary_of_contract", name=st.session_state.arquivo_resumido))
        st.markdown(st.session_state.resumo_gerado)

