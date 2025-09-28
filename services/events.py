import streamlit as st
import time
from datetime import datetime
from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from core.schemas import ListaDeEventos

@st.cache_data(show_spinner="Extraindo prazos...")
def extrair_eventos_dos_contratos(docs: List[dict], google_api_key: str):
    if not docs or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    prompt = PromptTemplate.from_template(
        "Analise o contrato {arquivo_fonte} e extraia eventos e datas:\n{texto_contrato}\n\n{format_instructions}"
    )
    fixer = OutputFixingParser.from_llm(parser=parser, llm=llm)

    eventos = []
    barra = st.progress(0)

    for i, doc in enumerate(docs):
        barra.progress((i+1)/len(docs), text=f"Processando {doc['nome']}...")
        try:
            resposta = llm.invoke([prompt.format(
                texto_contrato=doc["texto"][:25000],
                arquivo_fonte=doc["nome"],
                format_instructions=parser.get_format_instructions()
            )])
            try:
                parsed = parser.parse(resposta.content)
            except:
                parsed = fixer.parse(resposta.content)

            for e in parsed.eventos:
                try:
                    data_obj = datetime.strptime(e.data_evento_str, "%Y-%m-%d").date()
                except:
                    data_obj = None
                eventos.append({
                    "Arquivo": doc["nome"],
                    "Evento": e.descricao_evento,
                    "Data": e.data_evento_str,
                    "DataObj": data_obj,
                    "Trecho": e.trecho_relevante
                })
        except Exception as e:
            eventos.append({"Arquivo": doc["nome"], "Evento": f"Erro {e}"})
        time.sleep(1)
    barra.empty()
    return eventos
