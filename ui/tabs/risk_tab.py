import streamlit as st
import time
from core.analysis import analisar_documento_para_riscos
from core.utils import get_full_text_from_pdf

def render():
    st.header("🚩 Análise de Cláusulas de Risco")
    st.markdown("Analisa os documentos em busca de cláusulas potencialmente arriscadas.")
    
    original_files = st.session_state.get("arquivos_pdf_originais")

    if not original_files:
        st.warning("Esta função requer o upload de novos arquivos na barra lateral para garantir a leitura do texto completo.")
        return

    if st.button("🔎 Analisar Riscos em Todos os Documentos", key="btn_analyze_risks", use_container_width=True):
        st.session_state.analise_riscos_resultados = {}
        
        full_texts = []
        for file in original_files:
            text = get_full_text_from_pdf(file)
            if text:
                full_texts.append({"nome": file.name, "texto": text})
        
        if not full_texts:
            st.warning("Nenhum texto pôde ser extraído dos documentos para análise.")
            return

        progress_bar = st.progress(0, text="Analisando riscos...")
        results = {}
        for i, doc_info in enumerate(full_texts):
            progress_bar.progress((i + 1) / len(full_texts), text=f"Analisando: {doc_info['nome']}...")
            result = analisar_documento_para_riscos(doc_info["texto"], doc_info["nome"])
            results[doc_info["nome"]] = result
            time.sleep(1.5)
        
        progress_bar.empty()
        st.session_state.analise_riscos_resultados = results
        st.success("Análise de riscos concluída.")
        st.rerun()

    if "analise_riscos_resultados" in st.session_state:
        st.markdown("---")
        for file_name, analysis in st.session_state.analise_riscos_resultados.items():
            with st.expander(f"Riscos Identificados em: {file_name}", expanded=True):
                st.markdown(analysis)
