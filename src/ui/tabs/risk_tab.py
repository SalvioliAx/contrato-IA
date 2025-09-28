import time
import streamlit as st
from src.services import analysis

def render(api_key, t):
    """Renderiza a aba de Análise de Riscos."""
    st.header(t("risks.header"))
    st.markdown(t("risks.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.warning(t("warnings.upload_docs_for_risk_analysis"))
        return

    if st.button(t("risks.analyze_button"), use_container_width=True, key="btn_analise_riscos"):
        st.session_state.analise_riscos_resultados = {}
        textos_completos = []
        for arquivo in arquivos_originais:
            texto = analysis._get_full_text_from_upload(arquivo, t)
            if texto.strip():
                textos_completos.append({"nome": arquivo.name, "texto": texto})
        
        if textos_completos:
            resultados_temp = {}
            barra_progresso = st.progress(0)
            for i, doc_info in enumerate(textos_completos):
                barra_progresso.progress((i + 1) / len(textos_completos), text=t("info.analyzing_risks_in_file", file=doc_info['nome']))
                resultado = analysis.analisar_documento_para_riscos(
                    doc_info["texto"], doc_info["nome"], api_key, t
                )
                resultados_temp[doc_info["nome"]] = resultado
                time.sleep(1.5)
            
            barra_progresso.empty()
            st.session_state.analise_riscos_resultados = resultados_temp
            st.success(t("success.risk_analysis_complete"))
        else:
            st.warning(t("warnings.no_text_extracted_for_risk_analysis"))
        st.rerun()

    if "analise_riscos_resultados" in st.session_state and st.session_state.analise_riscos_resultados:
        st.markdown("---")
        for nome_arquivo, analise in st.session_state.analise_riscos_resultados.items():
            with st.expander(t("risks.expander_title", file=nome_arquivo), expanded=True):
                st.markdown(analise)
