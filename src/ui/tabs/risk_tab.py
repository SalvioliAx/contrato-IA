import streamlit as st
from src.services import analysis
from src.utils import get_full_text_from_uploads

def display_risk_tab(t):
    """Renderiza a aba de Análise de Riscos."""
    st.header(t("risks.header"))
    st.markdown(t("risks.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.info(t("info.upload_new_docs_for_risk_analysis"))
        return

    if st.button(t("risks.analyze_risks_button"), key="btn_risk_analysis", use_container_width=True):
        st.session_state.analise_riscos_resultados = {}
        
        textos_completos = get_full_text_from_uploads(arquivos_originais, t)
        
        resultados_temp = {}
        if textos_completos:
            barra_progresso = st.progress(0, text=t("info.analyzing_risks_progress"))
            for i, doc_info in enumerate(textos_completos):
                progresso = (i + 1) / len(textos_completos)
                barra_progresso.progress(progresso, text=t("info.analyzing_file_progress", name=doc_info["nome"]))
                
                resultado_doc = analysis.analisar_documento_para_riscos(doc_info["texto"], doc_info["nome"], t)
                resultados_temp[doc_info["nome"]] = resultado_doc
            
            barra_progresso.empty()
            st.session_state.analise_riscos_resultados = resultados_temp
            st.success(t("success.risk_analysis_complete"))
        else:
            st.warning(t("warnings.no_text_for_risk_analysis"))
        st.rerun()

    if st.session_state.get("analise_riscos_resultados"):
        st.markdown("---")
        for nome_arquivo, analise in st.session_state.analise_riscos_resultados.items():
            with st.expander(t("risks.expander_title", name=nome_arquivo), expanded=True):
                st.markdown(analise)

