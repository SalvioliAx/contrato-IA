import time
import streamlit as st
from src.services import analysis

def render(api_key, t):
    """Renderiza a aba de Verificação de Conformidade."""
    st.header(t("compliance.header"))
    st.markdown(t("compliance.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais or len(arquivos_originais) < 2:
        st.warning(t("warnings.upload_at_least_two_docs_for_compliance"))
        return

    nomes_arquivos = [f.name for f in arquivos_originais]
    col_ref, col_ana = st.columns(2)

    with col_ref:
        doc_ref_nome = st.selectbox(t("compliance.reference_doc_label"), options=nomes_arquivos, index=None, placeholder=t("compliance.reference_doc_placeholder"), key="select_doc_ref_conf")
    
    opcoes_analise = [n for n in nomes_arquivos if n != doc_ref_nome] if doc_ref_nome else []

    with col_ana:
        docs_ana_nomes = st.multiselect(t("compliance.analysis_docs_label"), options=opcoes_analise, placeholder=t("compliance.analysis_docs_placeholder"), key="multiselect_docs_ana_conf")

    if st.button(t("compliance.verify_button"), use_container_width=True, disabled=not (doc_ref_nome and docs_ana_nomes)):
        st.session_state.conformidade_resultados = {}
        
        doc_ref_obj = next((f for f in arquivos_originais if f.name == doc_ref_nome), None)
        texto_ref = analysis._get_full_text_from_upload(doc_ref_obj, t)

        if not texto_ref.strip():
            st.error(t("errors.read_error_reference_doc", file=doc_ref_nome))
            return

        barra_progresso = st.progress(0)
        for i, nome_doc in enumerate(docs_ana_nomes):
            barra_progresso.progress((i + 1) / len(docs_ana_nomes), text=t("info.analyzing_compliance_progress", file1=nome_doc, file2=doc_ref_nome))
            doc_ana_obj = next((f for f in arquivos_originais if f.name == nome_doc), None)
            texto_ana = analysis._get_full_text_from_upload(doc_ana_obj, t)
            
            if texto_ana.strip():
                resultado = analysis.verificar_conformidade_documento(
                    texto_ref, doc_ref_nome, texto_ana, nome_doc, api_key, t
                )
                st.session_state.conformidade_resultados[f"{nome_doc}_vs_{doc_ref_nome}"] = resultado
                time.sleep(2)
            else:
                st.error(t("errors.read_error_analysis_doc", file=nome_doc))
        
        barra_progresso.empty()
        st.success(t("success.compliance_analysis_complete"))
        st.rerun()

    if "conformidade_resultados" in st.session_state and st.session_state.conformidade_resultados:
        st.markdown("---")
        for chave, relatorio in st.session_state.conformidade_resultados.items():
            with st.expander(f"{t('compliance.report_expander_title')}: {chave.replace('_vs_', ' vs ')}", expanded=True):
                st.markdown(relatorio)
