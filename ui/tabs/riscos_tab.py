import streamlit as st
from services.summarizer import gerar_resumo_executivo
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def render_resumo_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Aba de Resumo / Executive Summary usando LangChain 2025.
    Permite selecionar um PDF e gerar um resumo executivo.
    """
    st.header(texts["summary_header"])

    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_carregados:
        st.info(texts["summary_info_load_docs"])
        return

    # Lista de nomes para selectbox
    nomes_arquivos = [f.name for f in arquivos_carregados]
    arquivo_selecionado_nome = st.selectbox(
        texts["summary_selectbox_label"],
        options=nomes_arquivos,
        index=None,
        placeholder=texts["summary_selectbox_placeholder"]
    )

    if arquivo_selecionado_nome:
        arquivo_obj = next((f for f in arquivos_carregados if f.name == arquivo_selecionado_nome), None)
        if arquivo_obj:
            if st.button(texts["summary_button"].format(filename=arquivo_selecionado_nome), use_container_width=True):
                with st.spinner(texts["spinner_generating_summary"]):
                    try:
                        arquivo_obj.seek(0)
                        pdf_bytes = arquivo_obj.read()
                        # Gera o resumo usando o serviço externo
                        resumo = gerar_resumo_executivo(pdf_bytes, arquivo_obj.name, google_api_key, lang_code)
                        st.markdown(resumo)
                        # Guarda o resumo no session_state caso queira reutilizar
                        st.session_state[f"resumo_{arquivo_selecionado_nome}"] = resumo
                    except Exception as e:
                        st.error(texts["summary_error"].format(filename=arquivo_selecionado_nome, e=e))
