import streamlit as st
from core.analysis import gerar_resumo_executivo
from core.utils import get_full_text_from_pdf

def render():
    st.header("📜 Resumo Executivo de um Contrato")
    
    original_files = st.session_state.get("arquivos_pdf_originais")

    if not original_files:
        st.warning("Esta função requer o upload de novos arquivos na barra lateral para gerar um resumo.")
        return

    file_names = [f.name for f in original_files]
    selected_file_name = st.selectbox(
        "Escolha um contrato para resumir:",
        options=file_names,
        index=None,
        key="select_summary_file",
        placeholder="Selecione um arquivo"
    )

    if st.button("✍️ Gerar Resumo Executivo", use_container_width=True, disabled=not selected_file_name):
        selected_file = next((f for f in original_files if f.name == selected_file_name), None)
        if selected_file:
            full_text = get_full_text_from_pdf(selected_file)
            if full_text:
                summary_text = gerar_resumo_executivo(full_text, selected_file.name)
                st.session_state.resumo_gerado = summary_text
                st.session_state.arquivo_resumido = selected_file.name
                st.rerun()
            else:
                st.error(f"Não foi possível extrair texto do arquivo {selected_file.name} para criar o resumo.")
        else:
            st.error("Arquivo selecionado não encontrado.")
    
    # Exibe o resumo se ele corresponder ao arquivo selecionado
    if st.session_state.get("arquivo_resumido") == selected_file_name and st.session_state.get("resumo_gerado"):
        st.subheader(f"Resumo do Contrato: {st.session_state.arquivo_resumido}")
        st.markdown(st.session_state.resumo_gerado)
