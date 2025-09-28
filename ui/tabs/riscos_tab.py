import streamlit as st
from services.risks import analisar_documento_para_riscos
import fitz

def render_riscos_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["risks_header"])

    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_carregados:
        st.info(texts["risks_info_load_docs"])
        return

    nomes_arquivos = [f.name for f in arquivos_carregados]
    arquivo_selecionado_nome = st.selectbox(
        texts["risks_selectbox_label"],
        options=nomes_arquivos,
        index=None,
        placeholder=texts["risks_selectbox_placeholder"]
    )
    
    if arquivo_selecionado_nome:
        arquivo_obj = next((f for f in arquivos_carregados if f.name == arquivo_selecionado_nome), None)
        if arquivo_obj:
            if st.button(texts["risks_button"].format(filename=arquivo_selecionado_nome), use_container_width=True):
                with st.spinner(texts["spinner_analyzing_risks"]):
                    texto_completo = ""
                    try:
                        arquivo_obj.seek(0)
                        pdf_bytes = arquivo_obj.read()
                        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                            for page in doc:
                                texto_completo += page.get_text() + "\n"
                    except Exception as e:
                        st.error(texts["risks_error_extract"].format(e=e))
                        return

                    if texto_completo.strip():
                        relatorio = analisar_documento_para_riscos(texto_completo, arquivo_obj.name, google_api_key, lang_code)
                        st.markdown(relatorio)
                    else:
                        st.warning(texts["risks_warning_no_text"])

