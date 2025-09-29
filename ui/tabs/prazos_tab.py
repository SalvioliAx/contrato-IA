import streamlit as st
from services.events import extrair_eventos_dos_contratos
import pandas as pd
import fitz # PyMuPDF
from locale import get_translation # Importa a função de tradução

# Alias para a função de tradução
T = get_translation

def render_prazos_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Prazos e Eventos, usando os arquivos da sessão.
    """
    # Localizado
    st.header(T("deadlines_header"))
    st.markdown(T("deadlines_markdown"))

    # MODIFICADO: Usa arquivos da sessão, não os dados extraídos do dashboard
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    
    if not arquivos_carregados:
        st.info(T("deadlines_info_load_docs")) # Localizado
        return

    # Localizado
    if st.button(T("deadlines_button_extract"), use_container_width=True):
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
                    # Localizado e formatado
                    st.warning(T("deadlines_warning_no_text").format(filename=arquivo.name))
            except Exception as e:
                # Localizado e formatado
                st.error(T("deadlines_error_read").format(filename=arquivo.name, e=e))

        if documentos_com_texto:
            # A função extrair_eventos_dos_contratos agora lida com sua própria localização
            eventos = extrair_eventos_dos_contratos(documentos_com_texto, google_api_key)
            if eventos:
                df_eventos = pd.DataFrame(eventos)
                # Converte a coluna de data para o formato datetime para ordenação
                df_eventos['DataObj'] = pd.to_datetime(df_eventos['DataObj'], errors='coerce')
                df_eventos_sorted = df_eventos.sort_values(by="DataObj", ascending=True, na_position='last')
                st.session_state.eventos_extraidos = df_eventos_sorted
            else:
                st.warning(T("deadlines_warning_no_events")) # Localizado
    
    if "eventos_extraidos" in st.session_state:
        # Exibe a tabela de prazos encontrados
        st.subheader(T("deadlines_subheader_table"))
        st.dataframe(st.session_state.eventos_extraidos, use_container_width=True)
        
        # Opcional: Visualização cronológica (se houver dados válidos)
        df_eventos = st.session_state.eventos_extraidos.dropna(subset=['DataObj'])
        if not df_eventos.empty:
            st.subheader(T("deadlines_subheader_chart"))
            
            # Gráfico de barras simples para contagem de eventos por ano/mês
            df_eventos['AnoMes'] = df_eventos['DataObj'].dt.to_period('M').astype(str)
            contagem_eventos = df_eventos.groupby('AnoMes').size().reset_index(name=T("deadlines_chart_y_axis"))
            
            st.bar_chart(
                contagem_eventos, 
                x='AnoMes', 
                y=T("deadlines_chart_y_axis"),
                x_label=T("deadlines_chart_x_axis"),
                y_label=T("deadlines_chart_y_axis")
            )
