import streamlit as st
from services.events import extrair_eventos_dos_contratos
import pandas as pd
import fitz

def render_prazos_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Renderiza a aba de Prazos e Eventos com textos localizados.
    """
    st.header(texts["deadlines_header"])

    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_carregados:
        st.info(texts["deadlines_info_load_docs"])
        return

    if st.button(texts["deadlines_button"], use_container_width=True):
        documentos_com_texto = []
        for arquivo in arquivos_carregados:
            try:
                arquivo.seek(0)
                pdf_bytes = arquivo.read()
                texto_completo = ""
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    for page in doc:
                        texto_completo += page.get_text() + "\n"
                if texto_completo.strip():
                    documentos_com_texto.append({"nome": arquivo.name, "texto": texto_completo})
                else:
                    st.warning(texts["deadlines_warning_no_text"].format(filename=arquivo.name))
            except Exception as e:
                st.error(texts["deadlines_error_read"].format(filename=arquivo.name, e=e))

        if documentos_com_texto:
            eventos = extrair_eventos_dos_contratos(documentos_com_texto, google_api_key, lang_code)
            if eventos:
                df_eventos = pd.DataFrame(eventos)
                df_eventos['DataObj'] = pd.to_datetime(df_eventos['DataObj'], errors='coerce')
                st.session_state.eventos_extraidos = df_eventos.sort_values(by="DataObj", ascending=True, na_position='last')
            else:
                st.warning(texts["deadlines_warning_no_events"])
    
    if "eventos_extraidos" in st.session_state:
        st.dataframe(st.session_state.eventos_extraidos, use_container_width=True)

