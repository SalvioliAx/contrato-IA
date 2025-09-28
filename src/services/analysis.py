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

from src.models import InfoContrato, ListaDeEventos, EventoContratual

# --- EXTRAÇÃO DE DADOS ESTRUTURADOS ---

@st.cache_data(show_spinner=False)
def extrair_dados_dos_contratos(_vector_store, _nomes_arquivos: list, _t) -> list:
    """Extrai dados estruturados de múltiplos contratos usando um vector store."""
    if not _vector_store or not _nomes_arquivos:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    resultados_finais = []
    
    # Mapeamento dos campos para extração com as perguntas traduzíveis
    mapa_campos = {
        "nome_banco_emissor": "analysis.bank_name_question",
        "valor_principal_numerico": "analysis.principal_value_question",
        "prazo_total_meses": "analysis.term_months_question",
        "taxa_juros_anual_numerica": "analysis.interest_rate_question",
        "possui_clausula_rescisao_multa": "analysis.termination_fee_question",
        "condicao_limite_credito": "analysis.credit_limit_condition_question",
        "condicao_juros_rotativo": "analysis.revolving_interest_condition_question",
        "condicao_anuidade": "analysis.annuity_condition_question",
        "condicao_cancelamento": "analysis.cancellation_condition_question"
    }
    
    total_operacoes = len(_nomes_arquivos) * len(mapa_campos)
    operacao_atual = 0
    barra_progresso = st.progress(0, text=_t("info.starting_extraction"))

    for nome_arquivo in _nomes_arquivos:
        dados_contrato_atual = {"arquivo_fonte": nome_arquivo}
        retriever_arquivo_atual = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )
        
        for campo, chave_pergunta in mapa_campos.items():
            operacao_atual += 1
            texto_progresso = _t("info.extracting_field_from_file", field=campo, filename=nome_arquivo, current=operacao_atual, total=total_operacoes)
            barra_progresso.progress(operacao_atual / total_operacoes, text=texto_progresso)
            
            pergunta_completa = _t(chave_pergunta)
            docs_relevantes = retriever_arquivo_atual.get_relevant_documents(pergunta_completa)
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs_relevantes])
            
            prompt_extracao = PromptTemplate.from_template(_t("analysis.extraction_prompt_template"))
            chain_extracao = LLMChain(llm=llm, prompt=prompt_extracao)
            
            if contexto.strip():
                try:
                    resultado = chain_extracao.invoke({"contexto": contexto, "pergunta": pergunta_completa})
                    resposta = resultado.get('text', '').strip()

                    # Lógica de processamento da resposta da IA
                    if campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
                        numeros = re.findall(r"[\d]+(?:[.,]\d+)*", resposta)
                        if numeros:
                            valor_str = numeros[0].replace('.', '').replace(',', '.')
                            if valor_str.count('.') > 1:
                                parts = valor_str.split('.')
                                valor_str = "".join(parts[:-1]) + "." + parts[-1]
                            dados_contrato_atual[campo] = float(valor_str)
                        else:
                            dados_contrato_atual[campo] = None
                    elif campo == "possui_clausula_rescisao_multa":
                        if any(x in resposta.lower() for x in ["sim", "yes", "sí"]): dados_contrato_atual[campo] = "Sim"
                        elif any(x in resposta.lower() for x in ["não", "nao", "no"]): dados_contrato_atual[campo] = "Não"
                        else: dados_contrato_atual[campo] = "Não claro"
                    else:
                        dados_contrato_atual[campo] = resposta if "não encontrado" not in resposta.lower() else "Não encontrado"
                except Exception:
                    dados_contrato_atual[campo] = "Erro na IA"
            else:
                dados_contrato_atual[campo] = "Contexto não encontrado"
            
            time.sleep(1.5)

        try:
            info_validada = InfoContrato(**dados_contrato_atual)
            resultados_finais.append(info_validada.model_dump())
        except Exception as e:
            st.error(f"Erro de validação Pydantic para {nome_arquivo}: {e}")
            resultados_finais.append({"arquivo_fonte": nome_arquivo, "nome_banco_emissor": "Erro de Validação"})
            
    barra_progresso.empty()
    return resultados_finais

# --- DETECÇÃO DE ANOMALIAS ---

def detectar_anomalias_no_dataframe(df: pd.DataFrame, _t) -> List[str]:
    """Detecta anomalias numéricas e categóricas no DataFrame de contratos."""
    if df.empty:
        return [_t("anomalies.no_data")]
    
    anomalias = []
    # Análise de outliers numéricos
    for campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
        if campo in df.columns:
            serie = pd.to_numeric(df[campo], errors='coerce').dropna()
            if len(serie) > 1:
                media, desvio_pad = serie.mean(), serie.std()
                if desvio_pad > 0:
                    limite_superior = media + 2 * desvio_pad
                    limite_inferior = media - 2 * desvio_pad
                    outliers = df[~serie.between(limite_inferior, limite_superior)]
                    for _, linha in outliers.iterrows():
                        anomalias.append(_t("anomalies.numeric_anomaly", file=linha['arquivo_fonte'], field=campo, value=linha[campo], mean=f"{media:.2f}"))

    # Análise de categorias raras
    for campo in ["possui_clausula_rescisao_multa", "nome_banco_emissor"]:
        if campo in df.columns and len(df) > 5:
            contagem = df[campo].value_counts(normalize=True)
            categorias_raras = contagem[contagem < 0.1]
            for categoria, freq in categorias_raras.items():
                docs_raros = df[df[campo] == categoria]['arquivo_fonte'].tolist()
                anomalias.append(_t("anomalies.categorical_anomaly", value=categoria, field=campo, percentage=f"{freq*100:.1f}", files=", ".join(docs_raros)))

    return anomalias if anomalias else [_t("anomalies.no_anomalies_found")]

# --- OUTRAS FUNÇÕES DE ANÁLISE (Resumo, Riscos, Prazos, Conformidade) ---

@st.cache_data(show_spinner=False)
def extrair_eventos_dos_contratos(_textos_completos: List[dict], _t) -> List[dict]:
    """Extrai datas e prazos importantes de uma lista de textos de documentos."""
    if not _textos_completos: return []

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    prompt_template = _t("analysis.events_prompt_template")
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["texto_contrato", "arquivo_fonte"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    todos_eventos = []

    for doc_info in _textos_completos:
        try:
            resultado = chain.invoke({"texto_contrato": doc_info["texto"][:25000], "arquivo_fonte": doc_info["nome"]})
            lista_eventos = parser.parse(resultado['text'])
            for evento in lista_eventos.eventos:
                todos_eventos.append({
                    "Arquivo Fonte": doc_info["nome"], "Evento": evento.descricao_evento,
                    "Data Informada": evento.data_evento_str, "Trecho Relevante": evento.trecho_relevante
                })
        except Exception as e:
            st.warning(f"Erro ao extrair eventos de {doc_info['nome']}: {e}")
        time.sleep(1)
        
    return todos_eventos

@st.cache_data(show_spinner=False)
def verificar_conformidade_documento(_texto_referencia, _nome_referencia, _texto_analisar, _nome_analisar, _t):
    """Compara um documento com um documento de referência para verificar conformidade."""
    if not _texto_referencia or not _texto_analisar: return _t("errors.missing_compliance_docs")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
    template = _t("analysis.compliance_prompt_template")
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        resultado = chain.invoke({
            "texto_doc_referencia": _texto_referencia[:25000], "nome_doc_referencia": _nome_referencia,
            "texto_doc_analisar": _texto_analisar[:25000], "nome_doc_analisar": _nome_analisar
        })
        return resultado.get('text', _t("errors.compliance_analysis_failed"))
    except Exception as e:
        return f"{_t('errors.compliance_analysis_failed')}: {e}"

@st.cache_data(show_spinner=False)
def gerar_resumo_executivo(_texto_completo, _t):
    """Gera um resumo executivo a partir do texto completo de um documento."""
    if not _texto_completo.strip(): return _t("errors.no_text_for_summary")
    
    llm_resumo = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
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

    llm_riscos = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
    template = _t("analysis.risk_prompt_template")
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(llm=llm_riscos, prompt=prompt)

    try:
        resultado = chain.invoke({"texto_contrato": _texto_completo[:30000], "nome_arquivo": _nome_arquivo})
        return resultado.get('text', _t("errors.risk_analysis_failed"))
    except Exception as e:
        return f"{_t('errors.risk_analysis_failed')}: {e}"

