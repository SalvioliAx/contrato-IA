import streamlit as st
import pandas as pd
from datetime import datetime
from src.services import analysis
from src.utils import get_full_text_from_uploads

def display_deadline_tab(t):
    """Renderiza a aba de Monitoramento de Prazos."""
    st.header(t("deadlines.header"))
    st.markdown(t("deadlines.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.info(t("info.upload_new_docs_for_deadline_analysis"))
        return

    if st.button(t("deadlines.analyze_deadlines_button"), key="btn_deadline_analysis", use_container_width=True):
        textos_completos = get_full_text_from_uploads(arquivos_originais, t)
        if textos_completos:
            eventos_extraidos = analysis.extrair_eventos_dos_contratos(textos_completos, t)
            if eventos_extraidos:
                df = pd.DataFrame(eventos_extraidos)
                df['Data Objeto'] = pd.to_datetime(df['Data Objeto'], errors='coerce')
                st.session_state.eventos_contratuais_df = df.sort_values(by="Data Objeto", ascending=True, na_position='last')
            else:
                st.session_state.eventos_contratuais_df = pd.DataFrame()
        else:
            st.warning(t("warnings.no_text_for_deadline_analysis"))
            st.session_state.eventos_contratuais_df = pd.DataFrame()
        st.rerun()

    if 'eventos_contratuais_df' in st.session_state and not st.session_state.eventos_contratuais_df.empty:
        df_display = st.session_state.eventos_contratuais_df.copy()
        
        df_display['Data Formatada'] = df_display['Data Objeto'].dt.strftime('%d/%m/%Y').fillna(t("deadlines.not_applicable"))
        
        st.subheader(t("deadlines.all_events_subheader"))
        colunas_exibir = ['Arquivo Fonte', 'Evento', 'Data Informada', 'Data Formatada', 'Trecho Relevante']
        st.dataframe(df_display[colunas_exibir], height=400, use_container_width=True)
        
        hoje = pd.Timestamp(datetime.now().date())
        proximos_90_dias = df_display[
            (df_display['Data Objeto'] >= hoje) &
            (df_display['Data Objeto'] <= (hoje + pd.Timedelta(days=90)))
        ]
        
        st.subheader(t("deadlines.upcoming_events_subheader"))
        if not proximos_90_dias.empty:
            st.table(proximos_90_dias[['Arquivo Fonte', 'Evento', 'Data Formatada']])
        else:
            st.info(t("info.no_upcoming_events"))

