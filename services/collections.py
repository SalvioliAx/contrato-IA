import streamlit as st
import json
from langchain.vectorstores import FAISS
from core.config import COLECOES_DIR

def listar_colecoes_salvas():
    """
    Lista os diretórios de coleções salvas.
    """
    if not COLECOES_DIR.exists():
        return []
    return [d.name for d in COLECOES_DIR.iterdir() if d.is_dir()]

def salvar_colecao_atual(nome_colecao, vector_store_atual, nomes_arquivos_atuais):
    """
    Salva o vector store e o manifesto de arquivos no disco.
    """
    if not nome_colecao.strip():
        st.error("Por favor, forneça um nome para a coleção.")
        return False

    caminho_colecao = COLECOES_DIR / nome_colecao
    try:
        caminho_colecao.mkdir(parents=True, exist_ok=True)
        # Salva o índice FAISS
        vector_store_atual.save_local(str(caminho_colecao / "faiss_index"))
        # Salva a lista de nomes de arquivos
        with open(caminho_colecao / "manifest.json", "w") as f:
            json.dump(nomes_arquivos_atuais, f)
        st.success(f"Coleção '{nome_colecao}' salva com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar coleção: {e}")
        return False

@st.cache_resource(show_spinner="Carregando coleção do disco...")
def carregar_colecao(nome_colecao, _embeddings_obj):
    """
    Carrega um vector store e seu manifesto a partir do disco.
    """
    caminho_colecao = COLECOES_DIR / nome_colecao
    caminho_indice = caminho_colecao / "faiss_index"
    caminho_manifesto = caminho_colecao / "manifest.json"

    if not caminho_indice.exists() or not caminho_manifesto.exists():
        st.error(f"Coleção '{nome_colecao}' está corrompida ou incompleta.")
        return None, None
    try:
        # Carrega o índice FAISS, permitindo deserialização
        vector_store = FAISS.load_local(
            str(caminho_indice),
            embeddings=_embeddings_obj,
            allow_dangerous_deserialization=True
        )
        # Carrega a lista de nomes de arquivos
        with open(caminho_manifesto, "r") as f:
            nomes_arquivos = json.load(f)
        st.success(f"Coleção '{nome_colecao}' carregada com sucesso!")
        return vector_store, nomes_arquivos
    except Exception as e:
        st.error(f"Erro ao carregar coleção '{nome_colecao}': {e}")
        return None, None
