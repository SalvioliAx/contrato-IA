import streamlit as st
import pandas as pd
from datetime import datetime
from core.analysis import extrair_eventos_dos_contratos
from core.utils import get_full_text_from_pdf

def render():
    st.header("🗓️ Monitoramento de Prazos e Vencimentos")
    st.markdown("Extrai e organiza datas e prazos importantes dos documentos carregados.")

    original_files = st.session_state.get("arquivos_pdf_originais")

    if not original_files:
        st.warning("Esta função requer o upload de novos arquivos na barra lateral para garantir a leitura do texto completo.")
        return

    if st.button("🔍 Analisar Prazos e Datas", key="btn_analyze_deadlines", use_container_width=True):
        full_texts = []
        for file in original_files:
            text = get_full_text_from_pdf(file)
            if text:
                full_texts.append({"nome": file.name, "texto": text})
        
        if full_texts:
            extracted_events = extrair_eventos_dos_contratos(full_texts)
            if extracted_events:
                df = pd.DataFrame(extracted_events)
                df['Data Objeto'] = pd.to_datetime(df['Data Objeto'], errors='coerce')
                st.session_state.eventos_contratuais_df = df.sort_values(by="Data Objeto", ascending=True, na_position='last')
            else:
                st.session_state.eventos_contratuais_df = pd.DataFrame()
        else:
            st.warning("Nenhum texto pôde ser extraído dos documentos para análise.")
            st.session_state.eventos_contratuais_df = pd.DataFrame()
        st.rerun()

    if 'eventos_contratuais_df' in st.session_state and not st.session_state.eventos_contratuais_df.empty:
        df_display = st.session_state.eventos_contratuais_df.copy()
        
        # Formata a data para exibição
        df_display['Data Formatada'] = df_display['Data Objeto'].dt.strftime('%d/%m/%Y').fillna('N/A')
        
        st.subheader("Todos os Eventos e Prazos Identificados")
        st.dataframe(
            df_display[['Arquivo Fonte', 'Evento', 'Data Informada', 'Data Formatada', 'Trecho Relevante']],
            use_container_width=True
        )

        st.subheader("Próximos Eventos (Próximos 90 dias)")
        today = pd.Timestamp(datetime.now().date())
        ninety_days_later = today + pd.Timedelta(days=90)
        
        upcoming_events = df_display[
            (df_display['Data Objeto'] >= today) &
            (df_display['Data Objeto'] <= ninety_days_later)
        ]

        if not upcoming_events.empty:
            st.table(upcoming_events[['Arquivo Fonte', 'Evento', 'Data Formatada']])
        else:
            st.info("Nenhum evento encontrado para os próximos 90 dias.")
