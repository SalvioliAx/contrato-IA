import streamlit as st
from services.events import extrair_eventos_dos_contratos 
import pandas as pd
import fitz # PyMuPDF
from typing import Dict, Any, List

# MODIFICADO: Adicionado 'texts' e 'lang' na assinatura da função para usar localização
def render_prazos_tab(embeddings_global: Any, google_api_key: str, texts: Dict[str, str], lang: str):
    """
    Renderiza a aba de Prazos e Eventos, usando os arquivos da sessão.
    Utiliza o dicionário 'texts' para todas as strings da UI.
    """
    # MODIFICADO: Usa chave localizada
    st.header(texts["deadlines_header"])
    st.markdown(texts["deadlines_markdown"])

    # Usa arquivos da sessão, não os dados extraídos do dashboard
    arquivos_carregados: List[st.runtime.uploaded_file_manager.UploadedFile] = st.session_state.get("arquivos_pdf_originais", [])
    
    if not arquivos_carregados:
        # MODIFICADO: Usa chave localizada
        st.info(texts["deadlines_info_load_docs"])
        return

    # MODIFICADO: Usa chave localizada para o botão (deadlines_button_extract)
    if st.button(texts["deadlines_button_extract"], use_container_width=True):
        documentos_com_texto = []
        
        # Extrai o texto completo de cada arquivo carregado
        # MODIFICADO: Usa chave localizada para o spinner
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
                        # MODIFICADO: Usa chave localizada para o warning
                        warning_text = texts["deadlines_warning_no_text"].format(filename=arquivo.name)
                        st.warning(warning_text)
                except Exception as e:
                    # MODIFICADO: Usa chave localizada para o erro
                    error_text = texts["deadlines_error_read"].format(filename=arquivo.name, e=e)
                    st.error(error_text)

            if documentos_com_texto:
                # MODIFICADO: Passa o dicionário 'texts' para a função de serviço
                eventos = extrair_eventos_dos_contratos(documentos_com_texto, google_api_key, texts)
                
                if eventos:
                    df_eventos = pd.DataFrame(eventos)
                    # Converte a coluna de data para o formato datetime para ordenação
                    # O tratamento de erros 'coerce' coloca NaT para datas inválidas
                    df_eventos['DataObj'] = pd.to_datetime(df_eventos['DataObj'], errors='coerce')
                    df_eventos_sorted = df_eventos.sort_values(by="DataObj", ascending=True, na_position='last')
                    st.session_state.eventos_extraidos = df_eventos_sorted
                else:
                    # MODIFICADO: Usa chave localizada para o warning
                    st.warning(texts["deadlines_warning_no_events"])
    
    if "eventos_extraidos" in st.session_state and not st.session_state.eventos_extraidos.empty:
        df_eventos_sorted = st.session_state.eventos_extraidos
        
        # MODIFICADO: Usa chave localizada
        st.subheader(texts["deadlines_subheader_table"])
        
        # Tabela de eventos (dropa 'DataObj' que é apenas para ordenação)
        st.dataframe(
            df_eventos_sorted.drop(columns=['DataObj']),
            use_container_width=True,
            column_order=("Arquivo", "Evento", "Data", "Trecho"),
            column_config={
                "Arquivo": st.column_config.Column(texts["chat_source_label"], help="Nome do arquivo fonte."),
                "Evento": st.column_config.Column("Descrição do Evento", help="Ação ou marco contratual."),
                "Data": st.column_config.TextColumn("Data Prevista", help="Data do evento (YYYY-MM-DD)."),
                "Trecho": st.column_config.LongTextColumn("Trecho de Referência", help="Excerto do contrato onde o evento foi encontrado.")
            }
        )

        # Gráfico (simplesmente mostrando as datas)
        df_chart = df_eventos_sorted.dropna(subset=['DataObj'])
        if not df_chart.empty:
            # Calcula os dias restantes para o gráfico (pode ser útil para visualização)
            df_chart['Dias Faltantes'] = (df_chart['DataObj'] - pd.Timestamp('today').normalize()).dt.days
            
            # MODIFICADO: Usa chave localizada
            st.subheader(texts["deadlines_subheader_chart"])
            
            # Cria um gráfico de barras simples para visualizar o tempo restante
            st.bar_chart(
                df_chart.sort_values(by='DataObj', ascending=False),
                x='Evento',
                y='Dias Faltantes',
                color='DataObj'
            )
        else:
            st.info("Nenhuma data válida encontrada para exibição no gráfico.")
