import sys
from pathlib import Path
import streamlit as st

# Adiciona o diretório 'src' ao sys.path para garantir que as importações funcionem
# em diferentes ambientes (local vs. Streamlit Cloud).
# Esta é uma prática robusta para projetos com subpastas.
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Importações dos módulos da aplicação (note que agora não usamos o prefixo 'src.')
from config import configure_page, initialize_session_state, get_api_key
from localization import Localization
from ui.sidebar import display_sidebar  # CORREÇÃO: Caminho correto para a sidebar
from services import document_processor

# Importações das abas da UI
from ui.tabs import chat_tab, dashboard_tab, summary_tab, risk_tab, deadline_tab, compliance_tab, anomaly_tab

def main():
    """Função principal que executa a aplicação Streamlit."""
    
    # --- 1. CONFIGURAÇÃO INICIAL DA PÁGINA E ESTADO ---
    configure_page()
    initialize_session_state()

    # Inicializa o gestor de localização (traduções)
    if 'localization' not in st.session_state:
        st.session_state.localization = Localization()

    # --- Seletor de Idioma ---
    cols = st.columns([0.8, 0.2])
    with cols[0]:
        st.title("💡 ContratIA")
    with cols[1]:
        lang_cols = st.columns(3)
        if lang_cols[0].button("🇧🇷 PT", use_container_width=True):
            st.session_state.language = "pt"
            st.rerun()
        if lang_cols[1].button("🇺🇸 EN", use_container_width=True):
            st.session_state.language = "en"
            st.rerun()
        if lang_cols[2].button("🇪🇸 ES", use_container_width=True):
            st.session_state.language = "es"
            st.rerun()

    st.session_state.localization.set_language(st.session_state.get("language", "pt"))
    t = st.session_state.localization.get_translator()
    
    # --- 2. GESTÃO DA API KEY E MODELO DE EMBEDDINGS ---
    google_api_key = get_api_key(t)
    embeddings_initialized = False
    initialization_error = None
    
    if google_api_key:
        try:
            st.session_state.embeddings_model = document_processor.get_embeddings_model(google_api_key)
            embeddings_initialized = True
        except ValueError as e:
            initialization_error = str(e)
    else:
        initialization_error = t("errors.api_key_or_embeddings_not_configured")

    # Renderiza a barra lateral
    display_sidebar(google_api_key, st.session_state.embeddings_model, t)

    # --- 3. LÓGICA DE EXIBIÇÃO DO CONTEÚDO PRINCIPAL ---
    if not embeddings_initialized:
        st.error(t("errors.critical_ia_model_failure"))
        st.warning(t("errors.possible_causes"))
        st.markdown(t("errors.what_to_do_markdown"))
        if initialization_error:
            st.error(f"**{t('errors.technical_error_title')}:** `{initialization_error}`")
        return

    # Define as abas da aplicação
    tab_keys = ["chat", "dashboard", "summary", "risks", "deadlines", "compliance", "anomalies"]
    tab_titles = [t(f"tabs.{key}") for key in tab_keys]
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

    with tab1:
        chat_tab.display_chat_tab(t)
    with tab2:
        dashboard_tab.display_dashboard_tab(t)
    with tab3:
        summary_tab.display_summary_tab(t)
    with tab4:
        risk_tab.display_risk_tab(t)
    with tab5:
        deadline_tab.display_deadline_tab(t)
    with tab6:
        compliance_tab.display_compliance_tab(t)
    with tab7:
        anomaly_tab.display_anomaly_tab(t)

if __name__ == "__main__":
    main()

