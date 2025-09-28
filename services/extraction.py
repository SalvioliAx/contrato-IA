import streamlit as st
import re, time
from typing import Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from services.dynamic_analyzer import identificar_pontos_chave_dinamicos

@st.cache_data(show_spinner="Extracting dynamic data from contracts...")
def extrair_dados_dos_contratos_dinamico(
    _vector_store: Optional[FAISS],
    _nomes_arquivos: list,
    textos_completos: str,
    google_api_key: str,
    lang_code: str  # Recebe o código do idioma
):
    if not _vector_store or not google_api_key or not _nomes_arquivos:
        return []

    pontos_chave = identificar_pontos_chave_dinamicos(textos_completos, google_api_key, lang_code)
    if not pontos_chave:
        st.warning("The AI could not identify key points for extraction. The dashboard will not be generated.")
        return []

    st.info(f"Dynamic fields identified by AI: {[p.campo for p in pontos_chave]}")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    resultados = []
    
    total_ops = len(_nomes_arquivos) * len(pontos_chave)
    op_atual = 0
    barra = st.empty()

    for nome_arquivo in _nomes_arquivos:
        dados = {"arquivo_fonte": nome_arquivo}
        retriever = _vector_store.as_retriever(search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5})

        for ponto in pontos_chave:
            op_atual += 1
            barra.progress(op_atual / total_ops, text=f"Extracting '{ponto.campo}' from {nome_arquivo}...")

            contexto = "\n\n---\n\n".join([doc.page_content for doc in retriever.get_relevant_documents(ponto.descricao)])
            prompt = PromptTemplate.from_template("Context:\n{contexto}\n\nBased on the context, answer concisely: {pergunta}\nAnswer:")
            chain = LLMChain(llm=llm, prompt=prompt)

            try:
                result = chain.invoke({"contexto": contexto, "pergunta": ponto.descricao})
                dados[ponto.campo] = result['text'].strip()
            except Exception as e:
                st.warning(f"Error in field {ponto.campo} for {nome_arquivo}: {e}")
                dados[ponto.campo] = "Extraction Error"
            time.sleep(1.2)

        resultados.append(dados)
    barra.empty()
    return resultados

