import streamlit as st
from src.services import analysis
from src.utils import get_full_text_from_uploads

def display_compliance_tab(t):
    """Renderiza a aba de Verificação de Conformidade."""
    st.header(t("compliance.header"))
    st.markdown(t("compliance.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais or len(arquivos_originais) < 2:
        st.info(t("info.upload_at_least_two_docs_for_compliance"))
        return

    nomes_arquivos = [f.name for f in arquivos_originais]
    col_ref, col_ana = st.columns(2)

    with col_ref:
        doc_referencia_nome = st.selectbox(
            t("compliance.reference_doc_label"),
            options=nomes_arquivos,
            key="select_compliance_ref",
            index=None,
            placeholder=t("compliance.reference_doc_placeholder")
        )
    
    opcoes_analise = [n for n in nomes_arquivos if n != doc_referencia_nome] if doc_referencia_nome else nomes_arquivos

    with col_ana:
        docs_a_analisar_nomes = st.multiselect(
            t("compliance.analysis_docs_label"),
            options=opcoes_analise,
            key="multiselect_compliance_ana",
            placeholder=t("compliance.analysis_docs_placeholder")
        )

    if st.button(t("compliance.verify_compliance_button"), key="btn_compliance_verify", use_container_width=True, disabled=not(doc_referencia_nome and docs_a_analisar_nomes)):
        st.session_state.conformidade_resultados = {}
        
        textos_completos = {doc['nome']: doc['texto'] for doc in get_full_text_from_uploads(arquivos_originais, t)}
        
        texto_doc_referencia = textos_completos.get(doc_referencia_nome)
        
        if not texto_doc_referencia:
            st.error(t("errors.could_not_read_reference_doc", name=doc_referencia_nome))
            return
            
        barra_progresso = st.progress(0, text=t("info.analyzing_compliance_progress"))
        resultados_temp = {}
        for i, nome_doc_analisar in enumerate(docs_a_analisar_nomes):
            progresso = (i + 1) / len(docs_a_analisar_nomes)
            barra_progresso.progress(progresso, text=t("info.comparing_docs_progress", ana=nome_doc_analisar, ref=doc_referencia_nome))
            
            texto_doc_analisar = textos_completos.get(nome_doc_analisar)
            if texto_doc_analisar:
                resultado = analysis.verificar_conformidade_documento(
                    texto_doc_referencia, doc_referencia_nome,
                    texto_doc_analisar, nome_doc_analisar, t
                )
                resultados_temp[f"{nome_doc_analisar}_vs_{doc_referencia_nome}"] = resultado
            else:
                st.warning(t("errors.could_not_read_analysis_doc", name=nome_doc_analisar))
        
        barra_progresso.empty()
        st.session_state.conformidade_resultados = resultados_temp
        st.success(t("success.compliance_analysis_complete"))
        st.rerun()

    if st.session_state.get("conformidade_resultados"):
        st.markdown("---")
        for chave, relatorio in st.session_state.conformidade_resultados.items():
            titulo = chave.replace("_vs_", f" {t('compliance.vs')} ")
            with st.expander(t("compliance.report_expander_title", title=titulo), expanded=True):
                st.markdown(relatorio)

