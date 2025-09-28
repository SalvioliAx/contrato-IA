import streamlit as st
import pandas as pd
from datetime import datetime
from src.utils import get_full_text_from_uploads
from src.services import analysis

def display_deadline_tab(t):
    """Renderiza a aba de Monitoramento de Prazos."""
    st.header(t("deadlines.header"))
    st.markdown(t("deadlines.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.info(t("info.upload_docs_for_deadlines"))
        return

    if st.button(t("deadlines.analyze_deadlines_button"), key="btn_deadline_analyze", use_container_width=True):
        textos_completos = get_full_text_from_uploads(arquivos_originais, t)
        if textos_completos:
            eventos_extraidos = analysis.extrair_eventos_dos_contratos(textos_completos, t)
            if eventos_extraidos:
                df_eventos = pd.DataFrame(eventos_extraidos)
                # Garante que a coluna 'Data Objeto' exista antes de converter
                if 'Data Objeto' in df_eventos.columns:
                    df_eventos['Data Objeto'] = pd.to_datetime(df_eventos['Data Objeto'], errors='coerce')
                    st.session_state.eventos_contratuais_df = df_eventos.sort_values(by="Data Objeto", ascending=True, na_position='last')
                else:
                    st.session_state.eventos_contratuais_df = df_eventos # Salva mesmo sem data
                st.success(t("success.deadline_analysis_complete"))
            else:
                st.session_state.eventos_contratuais_df = pd.DataFrame()
                st.warning(t("warnings.no_deadlines_extracted"))
        else:
            st.session_state.eventos_contratuais_df = pd.DataFrame()
            st.warning(t("warnings.no_text_for_deadlines"))
        st.rerun()

    df_display_eventos = st.session_state.get("eventos_contratuais_df")
    
    if df_display_eventos is not None and not df_display_eventos.empty:
        st.subheader(t("deadlines.all_events_subheader"))
        
        df_para_mostrar = df_display_eventos.copy()
        if 'Data Objeto' in df_para_mostrar.columns and pd.api.types.is_datetime64_any_dtype(df_para_mostrar['Data Objeto']):
            df_para_mostrar['Data Formatada'] = df_para_mostrar['Data Objeto'].dt.strftime('%d/%m/%Y').fillna('N/A')
        else:
            df_para_mostrar['Data Formatada'] = 'N/A'
            
        colunas_a_exibir = ['Arquivo Fonte', 'Evento', 'Data Informada', 'Data Formatada', 'Trecho Relevante']
        colunas_existentes = [col for col in colunas_a_exibir if col in df_para_mostrar.columns]
        st.dataframe(df_para_mostrar[colunas_existentes], height=400, use_container_width=True)

        if 'Data Objeto' in df_para_mostrar.columns and pd.api.types.is_datetime64_any_dtype(df_para_mostrar['Data Objeto']) and df_para_mostrar['Data Objeto'].notna().any():
            st.subheader(t("deadlines.upcoming_events_subheader"))
            hoje = pd.Timestamp(datetime.now().date())
            proximos_90_dias = hoje + pd.Timedelta(days=90)
            
            proximos_eventos = df_para_mostrar[
                (df_para_mostrar['Data Objeto'] >= hoje) &
                (df_para_mostrar['Data Objeto'] <= proximos_90_dias)
            ]
            
            if not proximos_eventos.empty:
                st.table(proximos_eventos[['Arquivo Fonte', 'Evento', 'Data Formatada']])
            else:
                st.info(t("info.no_upcoming_events"))
