import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def init_embeddings(api_key: str):
    """
    Inicializa e retorna o objeto de embeddings do Google Generative AI.
    """
    if not api_key:
        return None
    try:
        # Utiliza o modelo de embedding-001 para criar os vetores
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return embeddings
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar embeddings: {e}")
        return None
