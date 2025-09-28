import json
import streamlit as st
from pathlib import Path
from langchain.vectorstores import FAISS
from src.config import COLECOES_DIR

def listar_colecoes_salvas() -> list:
    """Retorna uma lista dos nomes das coleções de vetores salvas."""
    if not COLECOES_DIR.exists():
        return []
    return [d.name for d in COLECOES_DIR.iterdir() if d.is_dir()]

def salvar_colecao_atual(nome_colecao: str, vector_store_atual, nomes_arquivos_atuais: list, t) -> bool:
    """Salva a coleção de vetores e o manifesto de arquivos no disco."""
    if not nome_colecao.strip():
        st.error(t("errors.collection_name_required"))
        return False
    
    caminho_colecao = COLECOES_DIR / nome_colecao
    try:
        caminho_colecao.mkdir(parents=True, exist_ok=True)
        vector_store_atual.save_local(str(caminho_colecao / "faiss_index"))
        with open(caminho_colecao / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(nomes_arquivos_atuais, f)
        st.success(t("success.collection_saved", name=nome_colecao))
        return True
    except Exception as e:
        st.error(t("errors.collection_save_error", error=e))
        return False

@st.cache_resource(show_spinner="Carregando coleção...")
def carregar_colecao(nome_colecao: str, _embeddings_obj):
    """
    Carrega uma coleção de vetores e o manifesto do disco.
    A anotação de cache do Streamlit acelera o carregamento de coleções já usadas.
    """
    caminho_colecao = COLECOES_DIR / nome_colecao
    caminho_indice = caminho_colecao / "faiss_index"
    caminho_manifesto = caminho_colecao / "manifest.json"

    if not caminho_indice.exists() or not caminho_manifesto.exists():
        st.error(f"Coleção '{nome_colecao}' está incompleta ou corrompida.")
        return None, None
    try:
        vector_store = FAISS.load_local(
            str(caminho_indice), 
            embeddings=_embeddings_obj, 
            allow_dangerous_deserialization=True
        )
        with open(caminho_manifesto, "r", encoding="utf-8") as f:
            nomes_arquivos = json.load(f)
        
        st.success(f"Coleção '{nome_colecao}' carregada com sucesso!")
        return vector_store, nomes_arquivos
    except Exception as e:
        st.error(f"Erro ao carregar coleção '{nome_colecao}': {e}")
        return None, None
