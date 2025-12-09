import streamlit as st
from core.config import get_google_api_key, hide_streamlit_style
from core.embeddings import init_embeddings
from core.locale import TRANSLATIONS  # Importa o novo arquivo de traduções
from ui.sidebar import render_sidebar
from ui.tabs.chat_tab import render_chat_tab
from ui.tabs.dashboard_tab import render_dashboard_tab
from ui.tabs.resumo_tab import render_resumo_tab
from ui.tabs.riscos_tab import render_riscos_tab
from ui.tabs.prazos_tab import render_prazos_tab
from ui.tabs.conformidade_tab import render_conformidade_tab
from ui.tabs.anomalias_tab import render_anomalias_tab

# Configuração inicial da página
st.set_page_config(layout="wide", page_title="ContratIA", page_icon="💡")

# --- GERENCIAMENTO DE IDIOMA ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'pt' # Idioma padrão

# Mapeamento para o seletor
lang_map = {"Português": "pt", "English": "en", "Español": "es"}
lang_map_inv = {v: k for k, v in lang_map.items()}

# Seletor de idioma na barra lateral
selected_lang_label = st.sidebar.selectbox(
    label="Idioma / Language",
    options=lang_map.keys(),
    index=list(lang_map.values()).index(st.session_state['lang']) # Define a seleção atual
)
st.session_state['lang'] = lang_map[selected_lang_label]
texts = TRANSLATIONS[st.session_state['lang']] # Carrega os textos do idioma selecionado

# --- INICIALIZAÇÃO E RENDERIZAÇÃO ---
hide_streamlit_style()
st.title(texts["app_title"])

google_api_key = get_google_api_key()
embeddings_global = init_embeddings(google_api_key)

# Passa os textos para a barra lateral
render_sidebar(embeddings_global, google_api_key, texts)

documentos_prontos = google_api_key and embeddings_global and st.session_state.get("vector_store_atual")

if not (google_api_key and embeddings_global):
    st.error(texts["error_api_key"])
elif not documentos_prontos:
    st.info(texts["info_load_docs"])
else:
    # Usa os textos para os nomes das abas
    tab_titles = [
        texts["tab_chat"], texts["tab_dashboard"], texts["tab_summary"],
        texts["tab_risks"], texts["tab_deadlines"], texts["tab_compliance"],
        texts["tab_anomalies"]
    ]
    tab_chat, tab_dashboard, tab_resumo, tab_riscos, tab_prazos, tab_conformidade, tab_anomalias = st.tabs(tab_titles)

    # Passa os textos e o código do idioma para cada aba
    lang_code = st.session_state['lang']
    
    with tab_chat:
        render_chat_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_dashboard:
        render_dashboard_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_resumo:
        render_resumo_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_riscos:
        render_riscos_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_prazos:
        render_prazos_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_conformidade:
        render_conformidade_tab(embeddings_global, google_api_key, texts, lang_code)
    with tab_anomalias:
        render_anomalias_tab(embeddings_global, google_api_key, texts)


