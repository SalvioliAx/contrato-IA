import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def init_embeddings(api_key: str):
    if not api_key:
        return None
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return embeddings
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar embeddings: {e}")
        return None
