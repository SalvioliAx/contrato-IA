import streamlit as st
import pandas as pd
from datetime import datetime
from src.services import analysis

def render(api_key, t):
    """Renderiza a aba de Monitoramento de Prazos."""
    st.header(t("deadlines.header"))
    st.markdown(t("deadlines.description"))

    arquivos_originais = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_originais:
        st.warning(t("warnings.upload_docs_for_deadlines"))
        return

    if st.button(t("deadlines.analyze_button"), use_container_width=True, key="btn_analise_prazos"):
        textos_completos = []
        for arquivo in arquivos_originais:
            texto = analysis._get_full_text_from_upload(arquivo, t)
            if texto.strip():
                textos_completos.append({"nome": arquivo.name, "texto": texto})
        
        if textos_completos:
            eventos_extraidos = analysis.extrair_eventos_dos_contratos(textos_completos, api_key, t)
            if eventos_extraidos:
                df = pd.DataFrame(eventos_extraidos)
                df['Data Objeto'] = pd.to_datetime(df['Data Informada'], format='%Y-%m-%d', errors='coerce')
                st.session_state.eventos_contratuais_df = df.sort_values(by="Data Objeto", ascending=True, na_position='last')
                st.success(t("success.deadline_extraction_complete"))
            else:
                st.session_state.eventos_contratuais_df = pd.DataFrame()
                st.info(t("info.no_deadlines_extracted"))
        else:
            st.warning(t("warnings.no_text_extracted_for_deadlines"))
            st.session_state.eventos_contratuais_df = pd.DataFrame()
        st.rerun()

    if 'eventos_contratuais_df' in st.session_state and st.session_state.eventos_contratuais_df is not None:
        df_eventos = st.session_state.eventos_contratuais_df
        if not df_eventos.empty:
            st.subheader(t("deadlines.all_events_subheader"))
            st.dataframe(df_eventos.drop(columns=['Data Objeto']), height=400, use_container_width=True)

            df_futuro = df_eventos.dropna(subset=['Data Objeto'])
            if not df_futuro.empty:
                st.subheader(t("deadlines.upcoming_events_subheader"))
                hoje = pd.Timestamp(datetime.now().date())
                proximos_eventos = df_futuro[
                    (df_futuro['Data Objeto'] >= hoje) &
                    (df_futuro['Data Objeto'] <= (hoje + pd.Timedelta(days=90)))
                ].copy()
                
                if not proximos_eventos.empty:
                    proximos_eventos['Data Formatada'] = proximos_eventos['Data Objeto'].dt.strftime('%d/%m/%Y')
                    st.table(proximos_eventos[['Arquivo Fonte', 'Evento', 'Data Formatada']])
                else:
                    st.info(t("info.no_upcoming_events"))
