import streamlit as st
from core.config import get_google_api_key, hide_streamlit_style
from core.embeddings import init_embeddings
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
hide_streamlit_style()
st.title("💡 ContratIA")

# Inicialização da API key e do modelo de embeddings
google_api_key = get_google_api_key()
embeddings_global = init_embeddings(google_api_key)

# Renderiza a barra lateral
render_sidebar(embeddings_global, google_api_key)

# Verifica se os pré-requisitos para as abas estão prontos
documentos_prontos = google_api_key and embeddings_global and st.session_state.get("vector_store_atual")

# Estrutura das abas
if not (google_api_key and embeddings_global):
    st.error("Chave de API do Google ou o modelo de Embeddings não estão configurados. Verifique a barra lateral.")
elif not documentos_prontos:
    st.info("👈 Por favor, carregue e processe documentos PDF ou uma coleção existente na barra lateral para começar.")
else:
    # Definição das abas e suas respectivas funções de renderização
    tab_chat, tab_dashboard, tab_resumo, tab_riscos, tab_prazos, tab_conformidade, tab_anomalias = st.tabs([
        "💬 Chat", "📊 Dashboard", "📝 Resumo", "⚠️ Riscos", "⏳ Prazos", "✅ Conformidade", "🔎 Anomalias"
    ])

    with tab_chat:
        render_chat_tab(embeddings_global, google_api_key)

    with tab_dashboard:
        render_dashboard_tab(embeddings_global, google_api_key)

    with tab_resumo:
        render_resumo_tab(embeddings_global, google_api_key)

    with tab_riscos:
        render_riscos_tab(embeddings_global, google_api_key)

    with tab_prazos:
        render_prazos_tab(embeddings_global, google_api_key)

    with tab_conformidade:
        render_conformidade_tab(embeddings_global, google_api_key)

    with tab_anomalias:
        render_anomalias_tab(embeddings_global, google_api_key)
