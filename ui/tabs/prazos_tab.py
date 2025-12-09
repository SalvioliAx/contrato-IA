import streamlit as st
import pandas as pd
import fitz
from services.events import extrair_eventos_dos_contratos
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def render_prazos_tab(embeddings_global, google_api_key, texts, lang_code):
    """
    Aba de Prazos / Deadlines usando LangChain 2025.
    Extrai eventos de contratos e exibe tabela ordenada.
    """
    st.header(texts["deadlines_header"])

    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_carregados:
        st.info(texts["deadlines_info_load_docs"])
        return

    if st.button(texts["deadlines_button"], use_container_width=True):
        documentos_com_texto = []

        with st.spinner(texts["spinner_extracting_deadlines"]):
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
                # Extrai eventos usando serviço externo
                eventos = extrair_eventos_dos_contratos(documentos_com_texto, google_api_key, lang_code)
                if eventos:
                    df_eventos = pd.DataFrame(eventos)
                    if 'DataObj' in df_eventos.columns:
                        df_eventos['DataObj'] = pd.to_datetime(df_eventos['DataObj'], errors='coerce')
                        st.session_state.eventos_extraidos = df_eventos.sort_values(
                            by="DataObj", ascending=True, na_position='last'
                        )
                    else:
                        st.session_state.eventos_extraidos = pd.DataFrame(eventos)
                else:
                    st.warning(texts["deadlines_warning_no_events"])
    
    # Exibição da tabela de eventos
    if "eventos_extraidos" in st.session_state and not st.session_state.eventos_extraidos.empty:
        st.dataframe(st.session_state.eventos_extraidos, use_container_width=True)
