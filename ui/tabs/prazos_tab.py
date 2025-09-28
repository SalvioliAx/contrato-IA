import streamlit as st
from services.events import extrair_eventos_dos_contratos
import pandas as pd
import fitz # PyMuPDF

def render_prazos_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Prazos e Eventos, usando os arquivos da sessão.
    """
    st.header("⏳ Prazos e Eventos Contratuais")

    # MODIFICADO: Usa arquivos da sessão, não os dados extraídos do dashboard
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    
    if not arquivos_carregados:
        st.info("Carregue documentos na barra lateral para extrair prazos e eventos.")
        return

    if st.button("Extrair Prazos de Todos os Documentos", use_container_width=True):
        documentos_com_texto = []
        # Extrai o texto completo de cada arquivo carregado
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
                    st.warning(f"Não foi possível extrair texto de {arquivo.name} para análise de prazos.")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo {arquivo.name}: {e}")

        if documentos_com_texto:
            eventos = extrair_eventos_dos_contratos(documentos_com_texto, google_api_key)
            if eventos:
                df_eventos = pd.DataFrame(eventos)
                # Converte a coluna de data para o formato datetime para ordenação
                df_eventos['DataObj'] = pd.to_datetime(df_eventos['DataObj'], errors='coerce')
                df_eventos_sorted = df_eventos.sort_values(by="DataObj", ascending=True, na_position='last')
                st.session_state.eventos_extraidos = df_eventos_sorted
            else:
                st.warning("Nenhum evento ou prazo foi encontrado nos documentos.")
    
    if "eventos_extraidos" in st.session_state:
        st.dataframe(st.session_state.eventos_extraidos, use_container_width=True)
