import streamlit as st
import json
from pathlib import Path
from langchain.vectorstores import FAISS
from core.config import COLECOES_DIR

def listar_colecoes_salvas():
    if not COLECOES_DIR.exists():
        return []
    return [d.name for d in COLECOES_DIR.iterdir() if d.is_dir()]

def salvar_colecao_atual(nome_colecao, vector_store_atual, nomes_arquivos_atuais):
    if not nome_colecao.strip():
        st.error("Por favor, forneça um nome para a coleção.")
        return False

    caminho_colecao = COLECOES_DIR / nome_colecao
    try:
        caminho_colecao.mkdir(parents=True, exist_ok=True)
        vector_store_atual.save_local(str(caminho_colecao / "faiss_index"))
        with open(caminho_colecao / "manifest.json", "w") as f:
            json.dump(nomes_arquivos_atuais, f)
        st.success(f"Coleção '{nome_colecao}' salva com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar coleção: {e}")
        return False

@st.cache_resource(show_spinner="Carregando coleção...")
def carregar_colecao(nome_colecao, _embeddings_obj):
    caminho_colecao = COLECOES_DIR / nome_colecao
    caminho_indice = caminho_colecao / "faiss_index"
    caminho_manifesto = caminho_colecao / "manifest.json"

    if not caminho_indice.exists() or not caminho_manifesto.exists():
        st.error(f"Coleção '{nome_colecao}' incompleta.")
        return None, None
    try:
        vector_store = FAISS.load_local(
            str(caminho_indice),
            embeddings=_embeddings_obj,
            allow_dangerous_deserialization=True
        )
        with open(caminho_manifesto, "r") as f:
            nomes_arquivos = json.load(f)
        st.success(f"Coleção '{nome_colecao}' carregada!")
        return vector_store, nomes_arquivos
    except Exception as e:
        st.error(f"Erro ao carregar coleção '{nome_colecao}': {e}")
        return None, None
