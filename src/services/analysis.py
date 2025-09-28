import streamlit as st
import re
import time
from typing import Optional, List
import pandas as pd
import numpy as np
from datetime import datetime
import fitz # PyMuPDF
import base64

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI # NOME CORRIGIDO AQUI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.messages import AIMessage, HumanMessage

# Importações locais
from src.models import InfoContrato, ListaDeEventos

# --- EXTRAÇÃO DE DADOS PARA DASHBOARD ---
@st.cache_data(show_spinner=True)
def extrair_dados_dos_contratos(_vector_store, _nomes_arquivos: list, _t) -> list:
    if not _vector_store or not _nomes_arquivos: return []
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0) # NOME CORRIGIDO AQUI
    resultados_finais = []
    
    mapa_campos_para_extracao = {
        "nome_banco_emissor": (_t("analysis.q_banco"), _t("analysis.i_banco")),
        "valor_principal_numerico": (_t("analysis.q_valor"), _t("analysis.i_valor")),
        "prazo_total_meses": (_t("analysis.q_prazo"), _t("analysis.i_prazo")),
        "taxa_juros_anual_numerica": (_t("analysis.q_juros"), _t("analysis.i_juros")),
        "possui_clausula_rescisao_multa": (_t("analysis.q_multa"), _t("analysis.i_multa")),
        "condicao_limite_credito": (_t("analysis.q_limite"), _t("analysis.i_limite")),
        "condicao_juros_rotativo": (_t("analysis.q_rotativo"), _t("analysis.i_rotativo")),
        "condicao_anuidade": (_t("analysis.q_anuidade"), _t("analysis.i_anuidade")),
        "condicao_cancelamento": (_t("analysis.q_cancelamento"), _t("analysis.i_cancelamento"))
    }
    
    total_operacoes = len(_nomes_arquivos) * len(mapa_campos_para_extracao)
    barra_progresso = st.progress(0)
    operacao_atual = 0

    for nome_arquivo in _nomes_arquivos:
        dados_contrato_atual = {"arquivo_fonte": nome_arquivo}
        retriever_arquivo_atual = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )
        
        for campo, (pergunta_chave, instrucao_adicional) in mapa_campos_para_extracao.items():
            operacao_atual += 1
            progress_text = _t("analysis.progress_text", field=campo, file=nome_arquivo, current=operacao_atual, total=total_operacoes)
            barra_progresso.progress(operacao_atual / total_operacoes, text=progress_text)
            
            docs_relevantes = retriever_arquivo_atual.get_relevant_documents(pergunta_chave)
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs_relevantes])
            
            if contexto.strip():
                prompt_extracao = PromptTemplate.from_template(
                    "{instrucao}\n\n{contexto_label}:\n{contexto}\n\n{pergunta_label}: {pergunta}\n{resposta_label}:"
                )
                chain_extracao = LLMChain(llm=llm, prompt=prompt_extracao)
                try:
                    resultado = chain_extracao.invoke({
                        "instrucao": instrucao_adicional, "contexto_label": _t("analysis.context_label"),
                        "contexto": contexto, "pergunta_label": _t("analysis.question_label"),
                        "pergunta": pergunta_chave, "resposta_label": _t("analysis.answer_label")
                    })
                    resposta = resultado['text'].strip()
                    dados_contrato_atual[campo] = resposta
                except Exception as e:
                    dados_contrato_atual[campo] = "Erro na IA"
            else:
                dados_contrato_atual[campo] = _t("analysis.context_not_found")
            time.sleep(1.5)

        try:
            info_validada = InfoContrato(**dados_contrato_atual)
            resultados_finais.append(info_validada.model_dump())
        except Exception as e_pydantic:
            st.error(_t("analysis.error_pydantic", file=nome_arquivo, error=e_pydantic))
            resultados_finais.append({"arquivo_fonte": nome_arquivo, "nome_banco_emissor": "Erro de Validação"})
            
    barra_progresso.empty()
    return resultados_finais

def _extrair_texto_completo(pdf_bytes, nome_arquivo, _t):
    texto_completo = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz:
            texto_completo = "".join(page.get_text() for page in doc_fitz)
    except Exception as e:
        st.warning(_t("analysis.warning_pymupdf_failed", file=nome_arquivo, error=e))

    if not texto_completo.strip():
        st.info(_t("analysis.info_gemini_fallback", file=nome_arquivo))
        try:
            llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1) # NOME CORRIGIDO AQUI
            prompt_ocr = _t("analysis.prompt_ocr")
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_vision:
                for page_num in range(min(len(doc_vision), 5)):
                    page_obj = doc_vision.load_page(page_num)
                    pix = page_obj.get_pixmap(dpi=200)
                    base64_image = base64.b64encode(pix.tobytes("png")).decode('utf-8')
                    msg = HumanMessage(content=[{"type": "text", "text": prompt_ocr}, {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}])
                    
                    with st.spinner(_t("analysis.spinner_gemini_page", page=page_num+1, file=nome_arquivo)):
                        ai_msg = llm_vision.invoke([msg])
                    
                    if isinstance(ai_msg, AIMessage) and ai_msg.content and isinstance(ai_msg.content, str):
                        texto_completo += ai_msg.content + "\n\n"
                    time.sleep(1)
        except Exception as e_gemini:
            st.error(_t("analysis.error_gemini_extraction", file=nome_arquivo, error=e_gemini))
    
    return texto_completo.strip()


@st.cache_data(show_spinner=True)
def gerar_resumo_executivo(arquivo_pdf_bytes, nome_arquivo_original, _t):
    texto_completo = _extrair_texto_completo(arquivo_pdf_bytes, nome_arquivo_original, _t)
    if not texto_completo: return _t("analysis.error_no_text_for_summary", file=nome_arquivo_original)

    llm_resumo = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3) # NOME CORRIGIDO AQUI
    template_prompt_resumo = PromptTemplate.from_template(_t("analysis.prompt_summary"))
    chain_resumo = LLMChain(llm=llm_resumo, prompt=template_prompt_resumo)
    try:
        resultado = chain_resumo.invoke({"texto_contrato": texto_completo[:30000]})
        return resultado['text']
    except Exception as e:
        return _t("analysis.error_generating_summary", error=e)


@st.cache_data(show_spinner=True)
def analisar_documento_para_riscos(texto_completo_doc, nome_arquivo_doc, _t):
    if not texto_completo_doc: return _t("analysis.error_no_text_for_risk", file=nome_arquivo_doc)

    llm_riscos = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2) # NOME CORRIGIDO AQUI
    prompt_riscos_template = PromptTemplate.from_template(_t("analysis.prompt_risk"))
    chain_riscos = LLMChain(llm=llm_riscos, prompt=prompt_riscos_template)
    try:
        resultado = chain_riscos.invoke({"nome_arquivo": nome_arquivo_doc, "texto_contrato": texto_completo_doc[:30000]})
        return resultado['text']
    except Exception as e:
        return _t("analysis.error_analyzing_risk", file=nome_arquivo_doc, error=e)


@st.cache_data(show_spinner=True)
def extrair_eventos_dos_contratos(textos_completos_docs: List[dict], _t) -> List[dict]:
    if not textos_completos_docs: return []
    
    llm_eventos = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, request_timeout=120) # NOME CORRIGIDO AQUI
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    output_fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.0)) # NOME CORRIGIDO AQUI
    
    prompt_template_str = _t("analysis.prompt_events")
    prompt_eventos = PromptTemplate(
        template=prompt_template_str,
        input_variables=["texto_contrato", "arquivo_fonte"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain_eventos = prompt_eventos | llm_eventos
    
    todos_os_eventos = []
    barra_progresso = st.progress(0)
    
    for i, doc_info in enumerate(textos_completos_docs):
        nome_arquivo, texto_contrato = doc_info["nome"], doc_info["texto"]
        barra_progresso.progress((i + 1) / len(textos_completos_docs), text=_t("analysis.progress_events", file=nome_arquivo))
        try:
            resposta_ia_obj = chain_eventos.invoke({"texto_contrato": texto_contrato[:25000], "arquivo_fonte": nome_arquivo})
            resposta_ia_str = resposta_ia_obj.content
            
            try:
                resultado_parseado = parser.parse(resposta_ia_str)
            except Exception:
                resultado_parseado = output_fixing_parser.parse(resposta_ia_str)
            
            if isinstance(resultado_parseado, ListaDeEventos):
                todos_os_eventos.extend(evento.model_dump() for evento in resultado_parseado.eventos)

        except Exception as e:
            st.warning(_t("analysis.error_processing_events", file=nome_arquivo, error=e))
        time.sleep(1)
        
    barra_progresso.empty()
    return todos_os_eventos


@st.cache_data(show_spinner=True)
def verificar_conformidade_documento(texto_doc_referencia, nome_doc_referencia, texto_doc_analisar, nome_doc_analisar, _t):
    if not texto_doc_referencia or not texto_doc_analisar:
        return _t("analysis.error_missing_docs_compliance")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=180) # NOME CORRIGIDO AQUI
    prompt_template = PromptTemplate.from_template(_t("analysis.prompt_compliance"))
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    try:
        resultado = chain.invoke({
            "nome_doc_referencia": nome_doc_referencia, "texto_doc_referencia": texto_doc_referencia[:25000],
            "nome_doc_analisar": nome_doc_analisar, "texto_doc_analisar": texto_doc_analisar[:25000]
        })
        return resultado['text']
    except Exception as e:
        return _t("analysis.error_compliance_analysis", error=e)

def detectar_anomalias_no_dataframe(df: pd.DataFrame, _t) -> List[str]:
    if df.empty: return [_t("analysis.anomaly_no_data")]
    
    anomalias = []
    campos_numericos = ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]
    for campo in campos_numericos:
        if campo in df.columns:
            serie = pd.to_numeric(df[campo], errors='coerce').dropna()
            if len(serie) > 1:
                media, desvio_pad = serie.mean(), serie.std()
                if desvio_pad > 0:
                    limite_superior = media + 2 * desvio_pad
                    limite_inferior = media - 2 * desvio_pad
                    outliers = df[(pd.to_numeric(df[campo], errors='coerce') > limite_superior) | (pd.to_numeric(df[campo], errors='coerce') < limite_inferior)]
                    for _, linha in outliers.iterrows():
                        anomalias.append(_t("analysis.anomaly_numeric", file=linha['arquivo_fonte'], field=campo, value=linha[campo], mean=f"{media:.2f}"))
    
    if not anomalias: return [_t("analysis.anomaly_none_found")]
    return anomalias

