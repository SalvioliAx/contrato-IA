import streamlit as st
import pandas as pd
import numpy as np
import re
import time
from typing import List, Optional
from datetime import datetime

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas import InfoContrato, ListaDeEventos
from core.utils import get_llm

# --- EXTRAÇÃO DE DADOS ESTRUTURADOS ---

@st.cache_data(show_spinner="Extraindo dados detalhados dos contratos...")
def extrair_dados_dos_contratos(_vector_store: Optional, _nomes_arquivos: list) -> list:
    if not _vector_store or not st.session_state.get("google_api_key") or not _nomes_arquivos:
        return []
    
    llm = get_llm(temperature=0)
    if not llm: return []

    resultados_finais = []
    mapa_campos_para_extracao = {
        "nome_banco_emissor": ("Qual o nome principal do banco, instituição financeira ou empresa emissora deste contrato?", "Responda apenas com o nome. Se não encontrar, diga 'Não encontrado'."),
        "valor_principal_numerico": ("Qual o valor monetário principal ou limite de crédito central deste contrato?", "Se encontrar um valor, forneça apenas o número (ex: 10000.50). Se não encontrar, responda 'Não encontrado'."),
        "prazo_total_meses": ("Qual o prazo de vigência total deste contrato em meses? Se estiver em anos, converta para meses.", "Se encontrar, forneça apenas o número de meses. Se não encontrar, responda 'Não encontrado'."),
        "taxa_juros_anual_numerica": ("Qual a principal taxa de juros anual (ou facilmente conversível para anual) mencionada?", "Se encontrar, forneça apenas o número percentual (ex: 12.5). Se não encontrar, responda 'Não encontrado'."),
        "possui_clausula_rescisao_multa": ("Este contrato menciona explicitamente uma multa monetária ou percentual em caso de rescisão?", "Responda apenas com 'Sim', 'Não', ou 'Não claro'."),
        "condicao_limite_credito": ("Qual é a política ou condição para definir o limite de crédito?", "Resuma a política em uma ou duas frases. Se não encontrar, responda 'Não encontrado'."),
        "condicao_juros_rotativo": ("Sob quais condições os juros do crédito rotativo são aplicados?", "Resuma a regra em uma ou duas frases. Se não encontrar, responda 'Não encontrado'."),
        "condicao_anuidade": ("Qual é a política de cobrança da anuidade descrita no contrato?", "Resuma a política em uma ou duas frases. Se não encontrar, responda 'Não encontrado'."),
        "condicao_cancelamento": ("Quais são as regras para o cancelamento ou rescisão do contrato?", "Resuma as regras em uma ou duas frases. Se não encontrar, responda 'Não encontrado'.")
    }

    total_operacoes = len(_nomes_arquivos) * len(mapa_campos_para_extracao)
    progress_bar = st.progress(0, text="Iniciando extração de dados...")

    for i, nome_arquivo in enumerate(_nomes_arquivos):
        dados_contrato_atual = {"arquivo_fonte": nome_arquivo}
        retriever_arquivo = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )

        for j, (campo, (pergunta, instrucao)) in enumerate(mapa_campos_para_extracao.items()):
            op_atual = i * len(mapa_campos_para_extracao) + j + 1
            progress_bar.progress(op_atual / total_operacoes, text=f"Extraindo '{campo}' de {nome_arquivo}...")

            docs_relevantes = retriever_arquivo.get_relevant_documents(pergunta)
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs_relevantes])

            if not contexto.strip():
                dados_contrato_atual[campo] = None
                continue
            
            prompt_template = PromptTemplate.from_template(
                "Contexto: {contexto}\n\nPergunta: {pergunta}\n\n{instrucao}\nResposta:"
            )
            chain = LLMChain(llm=llm, prompt=prompt_template)
            
            try:
                resultado = chain.invoke({"contexto": contexto, "pergunta": pergunta, "instrucao": instrucao})
                resposta = resultado['text'].strip()
                
                # ... (lógica de parsing da resposta, idêntica à original) ...
                if campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
                    numeros = re.findall(r"[\d]+(?:[.,]\d+)*", resposta)
                    if numeros:
                        valor_str = numeros[0].replace('.', '').replace(',', '.')
                        if valor_str.count('.') > 1:
                            parts = valor_str.split('.')
                            valor_str = "".join(parts[:-1]) + "." + parts[-1]
                        
                        if campo == "prazo_total_meses":
                            dados_contrato_atual[campo] = int(float(valor_str))
                        else:
                            dados_contrato_atual[campo] = float(valor_str)
                    else:
                        dados_contrato_atual[campo] = None
                elif campo == "possui_clausula_rescisao_multa":
                    if "sim" in resposta.lower(): dados_contrato_atual[campo] = "Sim"
                    elif "não" in resposta.lower() or "nao" in resposta.lower(): dados_contrato_atual[campo] = "Não"
                    else: dados_contrato_atual[campo] = "Não claro"
                else:
                    dados_contrato_atual[campo] = resposta if "não encontrado" not in resposta.lower() else "Não encontrado"

            except Exception as e:
                st.warning(f"Erro ao invocar LLM para '{campo}' em {nome_arquivo}: {e}")
                dados_contrato_atual[campo] = "Erro na IA"
            time.sleep(1.5)

        try:
            info_validada = InfoContrato(**dados_contrato_atual)
            resultados_finais.append(info_validada.model_dump())
        except Exception as e_pydantic:
            st.error(f"Erro de validação Pydantic para {nome_arquivo}: {e_pydantic}")
            resultados_finais.append({"arquivo_fonte": nome_arquivo, "nome_banco_emissor": "Erro de Validação"})

    progress_bar.empty()
    st.success("Extração de dados para dashboard concluída!")
    return resultados_finais

# --- ANÁLISE DE ANOMALIAS ---

def detectar_anomalias_no_dataframe(df: pd.DataFrame) -> List[str]:
    # A lógica desta função permanece a mesma da original.
    anomalias_encontradas = []
    if df.empty: return ["Nenhum dado para analisar anomalias."]
    
    campos_numericos = ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]
    for campo in campos_numericos:
        if campo in df.columns:
            serie_numerica = pd.to_numeric(df[campo], errors='coerce').dropna()
            if len(serie_numerica) > 1:
                media = serie_numerica.mean(); desvio_pad = serie_numerica.std()
                if desvio_pad > 0:
                    limite_superior = media + 2 * desvio_pad; limite_inferior = media - 2 * desvio_pad
                    outliers = df[(serie_numerica < limite_inferior) | (serie_numerica > limite_superior)]
                    for _, linha in outliers.iterrows():
                        anomalias_encontradas.append(f"**Anomalia Numérica em `{linha['arquivo_fonte']}`:** Campo '{campo}' com valor `{linha[campo]}` está distante da média ({media:.2f}).")
    
    campos_categoricos = ["possui_clausula_rescisao_multa", "nome_banco_emissor"]
    for campo in campos_categoricos:
        if campo in df.columns:
            contagem_valores = df[campo].value_counts(normalize=True)
            if len(df) > 5:
                categorias_raras = contagem_valores[contagem_valores < 0.1]
                for categoria, freq in categorias_raras.items():
                    documentos = df[df[campo] == categoria]['arquivo_fonte'].tolist()
                    anomalias_encontradas.append(f"**Anomalia Categórica:** O valor '`{categoria}`' para '{campo}' é incomum (presente em {freq*100:.1f}% dos contratos: {', '.join(documentos[:3])}).")
    
    if not anomalias_encontradas: return ["Nenhuma anomalia significativa detectada."]
    return anomalias_encontradas

# --- ANÁLISES DE DOCUMENTO INDIVIDUAL ---

@st.cache_data(show_spinner="Gerando resumo executivo...")
def gerar_resumo_executivo(texto_completo, nome_arquivo):
    if not texto_completo.strip() or not st.session_state.get("google_api_key"):
        return f"Erro: Não foi possível ler o conteúdo do PDF {nome_arquivo} para resumo."
    
    llm = get_llm(temperature=0.3)
    if not llm: return "Erro: LLM não inicializado."

    template = PromptTemplate.from_template(
        "Você é um assistente especializado em resumir documentos jurídicos. "
        "Com base no texto do contrato fornecido, crie um resumo executivo em 5 a 7 tópicos (bullet points). "
        "Destaque: partes envolvidas, objeto, prazo, obrigações financeiras e condições de rescisão.\n\n"
        "TEXTO DO CONTRATO:\n{texto_contrato}\n\nRESUMO EXECUTIVO:"
    )
    chain = LLMChain(llm=llm, prompt=template)
    try:
        resultado = chain.invoke({"texto_contrato": texto_completo[:30000]})
        return resultado['text']
    except Exception as e:
        return f"Erro ao gerar resumo: {e}"

@st.cache_data(show_spinner="Analisando riscos no documento...")
def analisar_documento_para_riscos(texto_completo, nome_arquivo):
    if not texto_completo.strip() or not st.session_state.get("google_api_key"):
        return f"Erro: Conteúdo ou Chave API ausente para análise de riscos de '{nome_arquivo}'."

    llm = get_llm(temperature=0.2)
    if not llm: return "Erro: LLM não inicializado."

    template = PromptTemplate.from_template(
        "Você é um advogado especialista em análise de riscos contratuais. "
        "Analise o texto a seguir e identifique cláusulas ou omissões que representem riscos (Financeiro, Operacional, Legal, etc.).\n"
        "Para cada risco: 1. Descreva o risco. 2. Cite o trecho relevante. 3. Classifique o risco.\n"
        "Se nenhum risco for encontrado, declare isso explicitamente.\n\n"
        "TEXTO DO CONTRATO ({nome_arquivo}):\n{texto_contrato}\n\nANÁLISE DE RISCOS:"
    )
    chain = LLMChain(llm=llm, prompt=template)
    try:
        resultado = chain.invoke({"nome_arquivo": nome_arquivo, "texto_contrato": texto_completo[:30000]})
        return resultado['text']
    except Exception as e:
        return f"Erro ao analisar riscos: {e}"

@st.cache_data(show_spinner="Extraindo datas e prazos dos contratos...")
def extrair_eventos_dos_contratos(textos_completos_docs: List[dict]) -> List[dict]:
    if not textos_completos_docs or not st.session_state.get("google_api_key"): return []
    
    llm_eventos = get_llm(temperature=0)
    if not llm_eventos: return []

    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    output_fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=get_llm(temperature=0.0))
    
    prompt_template_str = """Analise o texto do contrato. Sua tarefa é identificar TODOS os eventos, datas e prazos.
Para cada evento, extraia:
1. 'descricao_evento': Descrição clara (ex: 'Data de assinatura').
2. 'data_evento_str': Data no formato YYYY-MM-DD. Se não for uma data exata, use a string 'Não Especificado'.
3. 'trecho_relevante': O trecho exato do contrato que menciona o evento.

{format_instructions}

TEXTO DO CONTRATO ({arquivo_fonte}):
{texto_contrato}

LISTA DE EVENTOS ENCONTRADOS:"""
    prompt = PromptTemplate(
        template=prompt_template_str,
        input_variables=["texto_contrato", "arquivo_fonte"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm_eventos

    todos_os_eventos = []
    progress_bar = st.progress(0, text="Analisando datas...")
    for i, doc_info in enumerate(textos_completos_docs):
        nome_arquivo, texto_contrato = doc_info["nome"], doc_info["texto"]
        progress_bar.progress((i + 1) / len(textos_completos_docs), text=f"Analisando datas em: {nome_arquivo}")
        try:
            resposta_ia = chain.invoke({"texto_contrato": texto_contrato[:25000], "arquivo_fonte": nome_arquivo})
            try:
                resultado_parseado = parser.parse(resposta_ia.content)
            except Exception:
                st.write(f"Parser inicial falhou para {nome_arquivo}, tentando correção...")
                resultado_parseado = output_fixing_parser.parse(resposta_ia.content)
            
            if isinstance(resultado_parseado, ListaDeEventos):
                for evento in resultado_parseado.eventos:
                    data_obj = None
                    if evento.data_evento_str and evento.data_evento_str.lower() != 'não especificado':
                        try:
                            data_obj = datetime.strptime(evento.data_evento_str, "%Y-%m-%d").date()
                        except ValueError: pass
                    
                    todos_os_eventos.append({
                        "Arquivo Fonte": nome_arquivo, "Evento": evento.descricao_evento,
                        "Data Informada": evento.data_evento_str, "Data Objeto": data_obj,
                        "Trecho Relevante": evento.trecho_relevante
                    })
        except Exception as e:
            st.warning(f"Erro ao processar datas para '{nome_arquivo}': {e}")
        time.sleep(1)
    
    progress_bar.empty()
    st.success("Extração de datas concluída!")
    return todos_os_eventos

@st.cache_data(show_spinner="Verificando conformidade do documento...")
def verificar_conformidade_documento(texto_referencia, nome_referencia, texto_analisar, nome_analisar):
    if not all([texto_referencia, texto_analisar, st.session_state.get("google_api_key")]):
        return "Erro: Documentos ou Chave API ausentes."
    
    llm = get_llm(temperature=0.1, timeout=180)
    if not llm: return "Erro: LLM não inicializado."

    template = PromptTemplate.from_template(
        "Você é um especialista em conformidade contratual. Compare o 'DOCUMENTO A ANALISAR' com o 'DOCUMENTO DE REFERÊNCIA'.\n"
        "Identifique cláusulas, termos ou omissões no 'DOCUMENTO A ANALISAR' que contradigam ou estejam em desalinhamento com o 'DOCUMENTO DE REFERÊNCIA'.\n"
        "Para cada conflito, descreva o problema, cite os trechos relevantes de ambos os documentos e explique o motivo do conflito.\n"
        "Se nenhum conflito for encontrado, declare isso explicitamente.\n\n"
        "DOCUMENTO DE REFERÊNCIA ({nome_referencia}):\n{texto_referencia}\n\n"
        "DOCUMENTO A ANALISAR ({nome_analisar}):\n{texto_analisar}\n\n"
        "RELATÓRIO DE ANÁLISE DE CONFORMIDADE:"
    )
    chain = LLMChain(llm=llm, prompt=template)
    try:
        resultado = chain.invoke({
            "nome_referencia": nome_referencia, "texto_referencia": texto_referencia[:25000],
            "nome_analisar": nome_analisar, "texto_analisar": texto_analisar[:25000]
        })
        return resultado['text']
    except Exception as e:
        return f"Erro ao gerar análise de conformidade: {e}"
