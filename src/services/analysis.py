import re
import time
import base64
import pandas as pd
import numpy as np
import streamlit as st
import fitz  # PyMuPDF
from typing import Optional, List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.messages import AIMessage, HumanMessage

from src.models import InfoContrato, ListaDeEventos

# --- FUNÇÕES DE EXTRAÇÃO DE DADOS ESTRUTURADOS ---

@st.cache_data(show_spinner="Extraindo dados detalhados dos contratos...")
def extrair_dados_dos_contratos(_vector_store: Optional["FAISS"], _nomes_arquivos: list, t) -> list:
    """Extrai informações estruturadas de múltiplos contratos para o dashboard."""
    if not _vector_store or not _nomes_arquivos:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    resultados_finais = []
    
    # Os prompts são agora obtidos do ficheiro de tradução
    mapa_campos_para_extracao = t("prompts.data_extraction_map")
    
    total_operacoes = len(_nomes_arquivos) * len(mapa_campos_para_extracao)
    barra_progresso = st.progress(0)
    texto_progresso = st.empty()
    op_atual = 0

    for nome_arquivo in _nomes_arquivos:
        dados_contrato_atual = {"arquivo_fonte": nome_arquivo}
        retriever_arquivo = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )
        
        for campo, prompts in mapa_campos_para_extracao.items():
            op_atual += 1
            barra_progresso.progress(op_atual / total_operacoes)
            texto_progresso.text(t("info.extracting_field_from_file", field=campo, file=nome_arquivo, current=op_atual, total=total_operacoes))
            
            docs = retriever_arquivo.get_relevant_documents(prompts["pergunta"] + " " + prompts["instrucao"])
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs])
            
            if contexto.strip():
                try:
                    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(t("prompts.data_extraction_chain.template")))
                    resultado = chain.invoke({
                        "instrucao": prompts["instrucao"],
                        "contexto": contexto, 
                        "pergunta": prompts["pergunta"]
                    })
                    resposta = resultado['text'].strip()

                    # Lógica de parsing da resposta
                    if campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
                        numeros = re.findall(r"[\d]+(?:[.,]\d+)*", resposta)
                        if numeros:
                            valor_str = numeros[0].replace('.', '').replace(',', '.')
                            if valor_str.count('.') > 1:
                                parts = valor_str.split('.')
                                valor_str = "".join(parts[:-1]) + "." + parts[-1]
                            dados_contrato_atual[campo] = float(valor_str) if campo != "prazo_total_meses" else int(float(valor_str))
                        else:
                            dados_contrato_atual[campo] = None
                    elif campo == "possui_clausula_rescisao_multa":
                        if any(term in resposta.lower() for term in ["sim", "yes", "sí"]):
                            dados_contrato_atual[campo] = "Sim"
                        elif any(term in resposta.lower() for term in ["não", "nao", "no"]):
                            dados_contrato_atual[campo] = "Não"
                        else:
                            dados_contrato_atual[campo] = "Não claro"
                    else:
                        dados_contrato_atual[campo] = resposta if "não encontrado" not in resposta.lower() else "Não encontrado"

                except Exception as e:
                    dados_contrato_atual[campo] = "Erro na IA"
            else:
                dados_contrato_atual[campo] = "Contexto não encontrado"
            
            time.sleep(1.5)

        try:
            info_validada = InfoContrato(**dados_contrato_atual)
            resultados_finais.append(info_validada.model_dump())
        except Exception as e:
            st.error(t("errors.pydantic_validation_error", file=nome_arquivo, error=e))
            resultados_finais.append({"arquivo_fonte": nome_arquivo, "nome_banco_emissor": "Erro de Validação"})
            
    barra_progresso.empty()
    texto_progresso.empty()
    return resultados_finais

# --- FUNÇÕES DE ANÁLISE DE CONTEÚDO (RISCOS, RESUMOS, ETC.) ---

def _get_full_text_from_upload(uploaded_file, t):
    """Extrai o texto completo de um objeto UploadedFile, com fallbacks."""
    nome_arquivo = uploaded_file.name
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    texto_completo = ""
    
    # 1. Tenta PyMuPDF
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            texto_completo = "".join(page.get_text() for page in doc)
    except Exception:
        pass # Falha silenciosa, tenta o próximo

    if texto_completo.strip():
        return texto_completo

    # 2. Tenta Gemini Vision como fallback
    st.info(t("info.fallback_to_gemini_full_text", file=nome_arquivo))
    try:
        llm_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc_fitz_vision:
            for page_num in range(len(doc_fitz_vision)):
                page_obj = doc_fitz_vision.load_page(page_num)
                pix = page_obj.get_pixmap(dpi=200)
                img_bytes_ocr = pix.tobytes("png")
                base64_image_ocr = base64.b64encode(img_bytes_ocr).decode('utf-8')
                human_message_ocr = HumanMessage(content=[
                    {"type": "text", "text": t("prompts.gemini_ocr.prompt")},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image_ocr}"}
                ])
                with st.spinner(t("info.gemini_processing_page", page=page_num + 1, total=len(doc_fitz_vision), file=nome_arquivo)):
                    ai_msg_ocr = llm_vision.invoke([human_message_ocr])
                if isinstance(ai_msg_ocr, AIMessage) and ai_msg_ocr.content:
                    texto_completo += ai_msg_ocr.content + "\n\n"
                time.sleep(1)
    except Exception as e:
        st.error(t("errors.gemini_vision_error", file=nome_arquivo, error=e))

    return texto_completo

@st.cache_data(show_spinner="Gerando resumo executivo...")
def gerar_resumo_executivo(uploaded_file, api_key, t):
    """Gera um resumo executivo de um único documento."""
    if not uploaded_file or not api_key:
        return t("errors.file_or_api_key_missing")
    
    texto_completo = _get_full_text_from_upload(uploaded_file, t)
    if not texto_completo.strip():
        return t("errors.text_extraction_failed_for_summary", file=uploaded_file.name)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
    prompt = PromptTemplate.from_template(t("prompts.summary.template"))
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        resultado = chain.invoke({"texto_contrato": texto_completo[:30000]})
        return resultado['text']
    except Exception as e:
        return t("errors.summary_generation_error", error=e)


@st.cache_data(show_spinner="Analisando riscos no documento...")
def analisar_documento_para_riscos(texto_completo, nome_arquivo, api_key, t):
    """Analisa um texto de contrato para identificar riscos."""
    if not texto_completo or not api_key:
        return t("errors.text_or_api_key_missing_for_analysis")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
    prompt = PromptTemplate.from_template(t("prompts.risk_analysis.template"))
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        resultado = chain.invoke({"nome_arquivo": nome_arquivo, "texto_contrato": texto_completo[:30000]})
        return resultado['text']
    except Exception as e:
        return t("errors.risk_analysis_error", file=nome_arquivo, error=e)

@st.cache_data(show_spinner="Extraindo datas e prazos dos contratos...")
def extrair_eventos_dos_contratos(textos_completos_docs: List[Dict], api_key, t) -> List[Dict]:
    """Extrai eventos e datas de uma lista de textos de documentos."""
    if not textos_completos_docs or not api_key:
        return []
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, request_timeout=120)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    output_fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
    
    prompt_template_str = t("prompts.event_extraction.template")
    prompt = PromptTemplate(
        template=prompt_template_str,
        input_variables=["texto_contrato", "arquivo_fonte"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm

    todos_eventos = []
    barra_progresso = st.progress(0)
    
    for i, doc_info in enumerate(textos_completos_docs):
        nome_arquivo, texto = doc_info["nome"], doc_info["texto"]
        barra_progresso.progress((i + 1) / len(textos_completos_docs), text=t("info.analyzing_deadlines_in_file", file=nome_arquivo))
        try:
            resposta_ia_obj = chain.invoke({"texto_contrato": texto[:25000], "arquivo_fonte": nome_arquivo})
            resposta_ia_str = resposta_ia_obj.content
            
            try:
                resultado_parseado = parser.parse(resposta_ia_str)
            except Exception:
                resultado_parseado = output_fixing_parser.parse(resposta_ia_str)
            
            if isinstance(resultado_parseado, ListaDeEventos):
                for evento in resultado_parseado.eventos:
                    todos_eventos.append({
                        "Arquivo Fonte": nome_arquivo,
                        "Evento": evento.descricao_evento,
                        "Data Informada": evento.data_evento_str,
                        "Trecho Relevante": evento.trecho_relevante
                    })
        except Exception as e:
            st.warning(t("errors.deadline_extraction_error", file=nome_arquivo, error=e))
        time.sleep(1)
        
    barra_progresso.empty()
    return todos_eventos

@st.cache_data(show_spinner="Verificando conformidade do documento...")
def verificar_conformidade_documento(texto_ref, nome_ref, texto_ana, nome_ana, api_key, t):
    """Compara um documento com outro de referência para verificar conformidade."""
    if not texto_ref or not texto_ana or not api_key:
        return t("errors.text_or_api_key_missing_for_analysis")
        
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1, request_timeout=180)
    prompt = PromptTemplate.from_template(t("prompts.compliance_check.template"))
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        resultado = chain.invoke({
            "nome_doc_referencia": nome_ref, "texto_doc_referencia": texto_ref[:25000],
            "nome_doc_analisar": nome_ana, "texto_doc_analisar": texto_ana[:25000]
        })
        return resultado['text']
    except Exception as e:
        return t("errors.compliance_analysis_error", file1=nome_ana, file2=nome_ref, error=e)

# --- FUNÇÃO DE DETECÇÃO DE ANOMALIAS ---

def detectar_anomalias_no_dataframe(df: pd.DataFrame, t) -> List[str]:
    """Detecta anomalias numéricas e categóricas no DataFrame de dados extraídos."""
    anomalias = []
    if df.empty:
        return [t("anomalies.no_data_to_analyze")]
    
    campos_numericos = ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]
    for campo in campos_numericos:
        if campo in df.columns:
            serie = pd.to_numeric(df[campo], errors='coerce').dropna()
            if len(serie) > 1:
                media, desvio_pad = serie.mean(), serie.std()
                if desvio_pad > 0:
                    limite_sup = media + 2 * desvio_pad
                    limite_inf = media - 2 * desvio_pad
                    outliers = df[(pd.to_numeric(df[campo], errors='coerce') > limite_sup) | (pd.to_numeric(df[campo], errors='coerce') < limite_inf)]
                    for _, linha in outliers.iterrows():
                        anomalias.append(t("anomalies.numerical_anomaly", file=linha['arquivo_fonte'], field=campo, value=linha[campo], mean=f"{media:.2f}"))

    campos_categoricos = ["possui_clausula_rescisao_multa", "nome_banco_emissor"]
    for campo in campos_categoricos:
        if campo in df.columns and len(df) > 5:
            contagem = df[campo].fillna("Não Especificado").value_counts(normalize=True)
            categorias_raras = contagem[contagem < 0.1]
            for categoria, freq in categorias_raras.items():
                docs = df[df[campo].fillna("Não Especificado") == categoria]['arquivo_fonte'].tolist()
                anomalias.append(t("anomalies.categorical_anomaly", value=categoria, field=campo, freq=f"{freq*100:.1f}", files=", ".join(docs[:3])))

    if not anomalias:
        return [t("anomalies.no_anomalies_found")]
    return anomalias
