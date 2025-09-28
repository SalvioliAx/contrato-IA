import streamlit as st
import time
from core.analysis import verificar_conformidade_documento
from core.utils import get_full_text_from_pdf

def render():
    st.header("⚖️ Verificador de Conformidade Contratual")
    st.markdown("Compare um documento com um documento de referência para identificar desalinhamentos.")

    original_files = st.session_state.get("arquivos_pdf_originais")
    if not original_files or len(original_files) < 2:
        st.warning("Carregue pelo menos dois documentos na barra lateral para usar esta função.")
        return

    file_names = [f.name for f in original_files]
    
    col1, col2 = st.columns(2)
    with col1:
        ref_doc_name = st.selectbox(
            "1. Documento de Referência:",
            options=file_names,
            index=None,
            key="select_ref_doc",
            placeholder="Selecione o doc. de referência"
        )
    with col2:
        analysis_doc_name = st.selectbox(
            "2. Documento a Analisar:",
            options=[n for n in file_names if n != ref_doc_name],
            index=None,
            key="select_analysis_doc",
            placeholder="Selecione o doc. para análise",
            disabled=not ref_doc_name
        )

    if st.button("🔎 Verificar Conformidade", use_container_width=True, disabled=not (ref_doc_name and analysis_doc_name)):
        ref_file = next((f for f in original_files if f.name == ref_doc_name), None)
        analysis_file = next((f for f in original_files if f.name == analysis_doc_name), None)

        if ref_file and analysis_file:
            ref_text = get_full_text_from_pdf(ref_file)
            analysis_text = get_full_text_from_pdf(analysis_file)
            
            if ref_text and analysis_text:
                result = verificar_conformidade_documento(
                    ref_text, ref_doc_name,
                    analysis_text, analysis_doc_name
                )
                st.session_state.conformidade_resultado = result
                st.session_state.conformidade_analise_key = f"{analysis_doc_name}_vs_{ref_doc_name}"
                st.rerun()
            else:
                st.error("Falha ao extrair texto de um ou ambos os documentos.")
        else:
            st.error("Erro interno ao localizar arquivos selecionados.")

    if "conformidade_resultado" in st.session_state:
        st.markdown("---")
        with st.expander(f"Relatório: {st.session_state.get('conformidade_analise_key', 'Análise')}", expanded=True):
            st.markdown(st.session_state.conformidade_resultado)
