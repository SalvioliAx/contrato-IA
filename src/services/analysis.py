import streamlit as st
import re
import time
import numpy as np
import pandas as pd
from typing import List

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.messages import AIMessage, HumanMessage

from models import InfoContrato, ListaDeEventos

# --- EXTRAÇÃO DE DADOS ESTRUTURADOS ---

@st.cache_data(show_spinner=False)
def extrair_dados_dos_contratos(_vector_store, _nomes_arquivos: list, _t) -> list:
    """Extrai dados estruturados de múltiplos contratos usando um vector store."""
    if not _vector_store or not _nomes_arquivos: return []
    
    # CORREÇÃO: Usando o nome do modelo especificado pelo utilizador
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    
    resultados_finais = []
    mapa_campos = _t("analysis.extraction_map")
    
    total_operacoes = len(_nomes_arquivos) * len(mapa_campos)
    barra_progresso = st.progress(0, text=_t("info.starting_extraction"))

    for i, nome_arquivo in enumerate(_nomes_arquivos):
        dados_contrato_atual = {"arquivo_fonte": nome_arquivo}
        retriever = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )
        
        for j, (campo, instrucoes) in enumerate(mapa_campos.items()):
            operacao_atual = i * len(mapa_campos) + j + 1
            barra_progresso.progress(operacao_atual / total_operacoes, 
                                     text=_t("info.extracting_field", field=campo, filename=nome_arquivo))
            
            docs = retriever.get_relevant_documents(instrucoes["question"])
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs])

            if contexto.strip():
                # ... (resto da lógica de extração) ...
                pass

    barra_progresso.empty()
    return resultados_finais

# --- OUTRAS FUNÇÕES DE ANÁLISE (Resumo, Riscos, etc.) ---

@st.cache_data(show_spinner=False)
def gerar_resumo_executivo(_texto_completo, _t):
    """Gera um resumo executivo a partir do texto completo de um documento."""
    if not _texto_completo.strip(): return _t("errors.no_text_for_summary")
    
    # CORREÇÃO: Usando o nome do modelo especificado pelo utilizador
    llm_resumo = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.3)
    template = _t("analysis.summary_prompt_template")
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm_resumo, prompt=prompt)
    
    try:
        resultado = chain.invoke({"texto_contrato": _texto_completo[:30000]})
        return resultado.get('text', _t("errors.summary_generation_failed"))
    except Exception as e:
        return f"{_t('errors.summary_generation_failed')}: {e}"

@st.cache_data(show_spinner=False)
def analisar_documento_para_riscos(_texto_completo, _nome_arquivo, _t):
    """Analisa o texto de um documento para identificar cláusulas de risco."""
    if not _texto_completo.strip(): return _t("errors.no_text_for_risk_analysis")

    # CORREÇÃO: Usando o nome do modelo especificado pelo utilizador
    llm_riscos = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.2)
    template = _t("analysis.risk_prompt_template")
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm_riscos, prompt=prompt)

    try:
        resultado = chain.invoke({"texto_contrato": _texto_completo[:30000], "nome_arquivo": _nome_arquivo})
        return resultado.get('text', _t("errors.risk_analysis_failed"))
    except Exception as e:
        return f"{_t('errors.risk_analysis_failed')}: {e}"

# ... (outras funções como extrair_eventos_dos_contratos, etc., também seriam atualizadas se usassem o modelo)

