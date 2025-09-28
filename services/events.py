import streamlit as st
import time
from datetime import datetime
from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from core.schemas import ListaDeEventos

# Nota: O prompt para extração de eventos é complexo e não está no locale.py por enquanto.
# A instrução de idioma será adicionada diretamente aqui.

@st.cache_data(show_spinner="Extraindo prazos...")
def extrair_eventos_dos_contratos(docs: List[dict], google_api_key: str, lang_code: str):
    """
    Extrai eventos e prazos dos contratos, instruindo a IA a descrevê-los no idioma correto.
    """
    if not docs or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    
    # Adicionando a instrução de idioma ao prompt
    prompt_template = (
        "Analise o contrato {arquivo_fonte} e extraia eventos e datas. "
        "A descrição de cada evento ('descricao_evento') deve ser em {language}.\n"
        "{texto_contrato}\n\n{format_instructions}"
    )
    
    prompt = PromptTemplate.from_template(prompt_template)
    fixer = OutputFixingParser.from_llm(parser=parser, llm=llm)

    eventos = []
    barra = st.empty()

    for i, doc in enumerate(docs):
        barra.progress((i + 1) / len(docs), text=f"Processando {doc['nome']}...")
        try:
            # Formatando o prompt com todas as variáveis, incluindo o idioma
            formatted_prompt = prompt.format(
                arquivo_fonte=doc["nome"],
                language=lang_code,
                texto_contrato=doc["texto"][:25000],
                format_instructions=parser.get_format_instructions()
            )
            
            resposta = llm.invoke(formatted_prompt)
            
            try:
                parsed = parser.parse(resposta.content)
            except Exception:
                parsed = fixer.parse(resposta.content)

            for e in parsed.eventos:
                try:
                    data_obj = datetime.strptime(e.data_evento_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    data_obj = None
                eventos.append({
                    "Arquivo": doc["nome"],
                    "Evento": e.descricao_evento,
                    "Data": e.data_evento_str,
                    "DataObj": data_obj,
                    "Trecho": e.trecho_relevante
                })
        except Exception as e:
            st.warning(f"Erro ao processar eventos em {doc['nome']}: {e}")
            eventos.append({"Arquivo": doc["nome"], "Evento": f"Erro {e}", "Data": "", "DataObj": None, "Trecho": ""})
        time.sleep(1.2)
        
    barra.empty()
    return eventos

