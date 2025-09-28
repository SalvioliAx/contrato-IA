import streamlit as st
import time
from datetime import datetime
from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from core.schemas import ListaDeEventos

@st.cache_data(show_spinner="Extracting deadlines and events from contracts...")
def extrair_eventos_dos_contratos(docs_com_texto: List[dict], google_api_key: str, lang_code: str):
    if not docs_com_texto or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    
    prompt = PromptTemplate.from_template(
        "Analyze the contract text '{arquivo_fonte}' and extract all important events, dates, and deadlines. The event description must be in {language}.\n"
        "Contract Text:\n{texto_contrato}\n\n{format_instructions}"
    )
    fixer = OutputFixingParser.from_llm(parser=parser, llm=llm)

    eventos = []
    barra = st.progress(0, "Starting deadline extraction...")

    for i, doc in enumerate(docs_com_texto):
        barra.progress((i + 1) / len(docs_com_texto), text=f"Analyzing deadlines in: {doc['nome']}...")
        try:
            resposta = llm.invoke(prompt.format(
                texto_contrato=doc["texto"][:25000],
                arquivo_fonte=doc["nome"],
                format_instructions=parser.get_format_instructions(),
                language=lang_code
            ))
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
                    "Arquivo": doc["nome"], "Evento": e.descricao_evento,
                    "Data": e.data_evento_str, "DataObj": data_obj, "Trecho": e.trecho_relevante
                })
        except Exception as e:
            st.warning(f"Error extracting events from {doc['nome']}: {e}")
        time.sleep(1)
    barra.empty()
    return eventos

