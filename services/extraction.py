import streamlit as st
import re, time
from typing import Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from services.dynamic_analyzer import identificar_pontos_chave_dinamicos

@st.cache_data(show_spinner="Extraindo dados dinâmicos dos contratos...")
def extrair_dados_dos_contratos_dinamico(
    _vector_store: Optional[FAISS],
    _nomes_arquivos: list,
    textos_completos: str,
    google_api_key: str
):
    """
    Orquestra a extração de dados: primeiro, identifica dinamicamente os campos
    relevantes com a IA e, em seguida, extrai o valor de cada campo para cada documento.
    """
    if not _vector_store or not google_api_key or not _nomes_arquivos:
        return []

    # Passo 1: Identificar dinamicamente os campos a serem extraídos
    pontos_chave = identificar_pontos_chave_dinamicos(textos_completos, google_api_key)
    if not pontos_chave:
        st.warning("A IA não conseguiu identificar pontos chave para extração. O dashboard não será gerado.")
        return []

    st.info(f"Campos dinâmicos identificados pela IA para o dashboard: {[p.campo for p in pontos_chave]}")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    resultados = []
    
    total_ops = len(_nomes_arquivos) * len(pontos_chave)
    op_atual = 0
    barra = st.empty()

    for nome_arquivo in _nomes_arquivos:
        dados = {"arquivo_fonte": nome_arquivo}
        retriever = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )

        # Passo 2: Extrair dados para cada campo identificado dinamicamente
        for ponto in pontos_chave:
            campo = ponto.campo
            pergunta = ponto.descricao
            
            op_atual += 1
            barra.progress(op_atual / total_ops, text=f"Extraindo '{campo}' de {nome_arquivo}...")

            docs = retriever.get_relevant_documents(pergunta)
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs])

            prompt = PromptTemplate.from_template(
                "Contexto:\n{contexto}\n\nCom base no contexto, responda de forma concisa: {pergunta}\nResposta:"
            )
            chain = LLMChain(llm=llm, prompt=prompt)

            try:
                result = chain.invoke({"contexto": contexto, "pergunta": pergunta})
                resposta = result['text'].strip()
                dados[campo] = resposta
            except Exception as e:
                st.warning(f"Erro no campo {campo} para {nome_arquivo}: {e}")
                dados[campo] = "Erro na extração"
            time.sleep(1.2) # Pausa para a API

        resultados.append(dados)
    barra.empty()
    return resultados

