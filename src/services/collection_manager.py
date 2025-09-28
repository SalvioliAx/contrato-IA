import streamlit as st
import json
from pathlib import Path
from langchain_community.vectorstores import FAISS

# Assume que COLECOES_DIR é definido em config.py e acessado de lá
from src.config import COLECOES_DIR

def listar_colecoes_salvas():
    """Lista os nomes das coleções de vetores salvas localmente."""
    if not COLECOES_DIR.exists():
        return []
    return [d.name for d in COLECOES_DIR.iterdir() if d.is_dir()]

def salvar_colecao_atual(nome_colecao, vector_store_atual, nomes_arquivos_atuais, t):
    """
    Salva o vector store e o manifesto da coleção atual no disco.
    Nota: esta função não é cacheada, por isso 't' não precisa de underscore.
    """
    if not nome_colecao.strip():
        st.error(t("collection_manager.error_provide_name"))
        return False
    
    caminho_colecao = COLECOES_DIR / nome_colecao
    try:
        caminho_colecao.mkdir(parents=True, exist_ok=True)
        vector_store_atual.save_local(str(caminho_colecao / "faiss_index"))
        with open(caminho_colecao / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(nomes_arquivos_atuais, f)
        st.success(t("collection_manager.success_collection_saved", name=nome_colecao))
        return True
    except Exception as e:
        st.error(t("collection_manager.error_saving_collection", error=e))
        return False

@st.cache_resource(show_spinner=True)
def carregar_colecao(nome_colecao, _embeddings_obj, _t):
    """
    Carrega uma coleção de vetores e seu manifesto a partir do disco.
    """
    st.info(_t("collection_manager.loading_collection", name=nome_colecao))
    caminho_colecao = COLECOES_DIR / nome_colecao
    caminho_indice = caminho_colecao / "faiss_index"
    caminho_manifesto = caminho_colecao / "manifest.json"

    if not caminho_indice.exists() or not caminho_manifesto.exists():
        st.error(_t("collection_manager.error_collection_incomplete", name=nome_colecao))
        return None, None
    
    try:
        vector_store = FAISS.load_local(
            str(caminho_indice), 
            embeddings=_embeddings_obj, 
            allow_dangerous_deserialization=True
        )
        with open(caminho_manifesto, "r", encoding="utf-8") as f:
            nomes_arquivos = json.load(f)
        
        st.success(_t("collection_manager.success_collection_loaded", name=nome_colecao))
        return vector_store, nomes_arquivos
    except Exception as e:
        st.error(_t("collection_manager.error_loading_collection", name=nome_colecao, error=e))
        return None, None

