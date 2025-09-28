import streamlit as st
from src.services import analysis
from src.utils import get_full_text_from_uploads # Usar texto completo para resumo

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
            # Em vez de passar bytes, extraímos o texto completo para consistência
            textos = get_full_text_from_uploads([arquivo_obj], t)
            if textos:
                texto_completo = textos[0]['texto']
                resumo = analysis.gerar_resumo_executivo(texto_completo, arquivo_obj.name, t)
                st.session_state.resumo_gerado = resumo
                st.session_state.arquivo_resumido = arquivo_selecionado_nome
                st.rerun()
            else:
                 st.error(t("errors.text_extraction_failed_for_file", filename=arquivo_obj.name))
        else:
            st.error(t("errors.file_not_found_in_session"))
    
    # Exibe o resumo se ele corresponder ao arquivo selecionado
    if st.session_state.get("arquivo_resumido") == arquivo_selecionado_nome and st.session_state.get("resumo_gerado"):
        st.subheader(t("summary.summary_of_contract", name=st.session_state.arquivo_resumido))
        st.markdown(st.session_state.resumo_gerado)
