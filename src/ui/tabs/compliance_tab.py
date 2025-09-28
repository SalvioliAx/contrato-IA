import streamlit as st
from src.utils import get_full_text_from_uploads
from src.services import analysis

def display_compliance_tab(t):
    """Renderiza a aba de Verificação de Conformidade."""
    st.header(t("compliance.header"))
    st.markdown(t("compliance.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais or len(arquivos_originais) < 2:
        st.info(t("info.upload_at_least_two_docs"))
        return

    nomes_arquivos = [f.name for f in arquivos_originais]
    col_ref, col_ana = st.columns(2)
    with col_ref:
        doc_referencia_nome = st.selectbox(
            t("compliance.reference_doc_label"),
            options=nomes_arquivos,
            key="select_doc_ref",
            index=None,
            placeholder=t("compliance.reference_doc_placeholder")
        )
    
    opcoes_analise = [n for n in nomes_arquivos if n != doc_referencia_nome] if doc_referencia_nome else nomes_arquivos
    
    with col_ana:
        docs_a_analisar_nomes = st.multiselect(
            t("compliance.analysis_docs_label"),
            options=opcoes_analise,
            key="multiselect_docs_ana",
            placeholder=t("compliance.analysis_docs_placeholder")
        )

    if st.button(t("compliance.verify_button"), key="btn_compliance_verify", use_container_width=True, disabled=not(doc_referencia_nome and docs_a_analisar_nomes)):
        doc_referencia_obj = next((arq for arq in arquivos_originais if arq.name == doc_referencia_nome), None)
        textos_completos_ref = get_full_text_from_uploads([doc_referencia_obj] if doc_referencia_obj else [], t)
        
        if not textos_completos_ref:
            st.error(t("errors.could_not_read_reference_doc", name=doc_referencia_nome))
            return

        texto_ref = textos_completos_ref[0]["texto"]
        docs_a_analisar_objs = [arq for arq in arquivos_originais if arq.name in docs_a_analisar_nomes]
        textos_completos_ana = get_full_text_from_uploads(docs_a_analisar_objs, t)
        
        resultados_temp = {}
        barra_progresso = st.progress(0, text=t("info.analyzing_compliance"))
        for i, doc_info in enumerate(textos_completos_ana):
            nome_doc_ana = doc_info["nome"]
            texto_doc_ana = doc_info["texto"]
            barra_progresso.progress((i + 1) / len(textos_completos_ana), text=t("info.analyzing_doc_vs_doc", doc1=nome_doc_ana, doc2=doc_referencia_nome))
            
            resultado = analysis.verificar_conformidade_documento(texto_ref, doc_referencia_nome, texto_doc_ana, nome_doc_ana, t)
            resultados_temp[f"{nome_doc_ana}_vs_{doc_referencia_nome}"] = resultado
        
        st.session_state.conformidade_resultados = resultados_temp
        barra_progresso.empty()
        st.success(t("success.compliance_analysis_complete"))
        st.rerun()

    resultados_finais = st.session_state.get("conformidade_resultados")
    if resultados_finais:
        st.markdown("---")
        for chave, relatorio in resultados_finais.items():
            with st.expander(t("compliance.report_expander_label", key=chave.replace('_vs_', ' vs ')), expanded=True):
                st.markdown(relatorio)
