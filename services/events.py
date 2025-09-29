import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from core.schemas import ListaDeEventos

# MODIFICADO: Remove st.cache_data devido ao argumento dinâmico 'texts'
def extrair_eventos_dos_contratos(docs_com_texto: List[dict], google_api_key: str, texts: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Usa um LLM com Pydantic para extrair datas e eventos de textos de contratos.
    Aceita o dicionário 'texts' para strings de UI localizadas.
    """
    if not docs_com_texto or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ListaDeEventos)
    prompt = PromptTemplate.from_template(
        "Analise o texto do contrato '{arquivo_fonte}' e extraia todos os eventos, datas e prazos importantes.\n"
        "Texto do Contrato:\n{texto_contrato}\n\n{format_instructions}"
    )
    fixer = OutputFixingParser.from_llm(parser=parser, llm=llm)

    eventos = []
    
    # MODIFICADO: Usa texto localizado para iniciar a barra de progresso
    barra = st.progress(0, texts["events_progress_extracting"]) 

    for i, doc in enumerate(docs_com_texto):
        # MODIFICADO: Usa texto localizado e formata com o nome do arquivo
        progress_text = texts["events_progress_analyzing"].format(filename=doc['nome'])
        barra.progress((i + 1) / len(docs_com_texto), text=progress_text)
        
        try:
            # Invoca o modelo com o prompt formatado
            # Limita o texto a 25000 caracteres para evitar estouro de token no prompt
            resposta = llm.invoke(prompt.format(
                texto_contrato=doc["texto"][:25000],
                arquivo_fonte=doc["nome"],
                format_instructions=parser.get_format_instructions()
            ))
            
            # Tenta fazer o parse da resposta; se falhar, usa o "fixer" para corrigir
            try:
                parsed = parser.parse(resposta.content)
            except Exception:
                parsed = fixer.parse(resposta.content)

            for e in parsed.eventos:
                try:
                    # Tenta converter a data para um objeto date para facilitar a ordenação e visualização
                    data_obj = datetime.strptime(e.data_evento_str, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    data_obj = None # Se a data não estiver no formato correto, armazena como None
                
                eventos.append({
                    "Arquivo": doc["nome"],
                    "Evento": e.descricao_evento,
                    "Data": e.data_evento_str,
                    "DataObj": data_obj,
                    "Trecho": e.trecho_relevante
                })
        except Exception as e:
            # MODIFICADO: Usa chave localizada para a mensagem de erro específica e genérica
            error_message = texts["events_warning_error"].format(filename=doc['nome'], e=e)
            st.warning(error_message)
            eventos.append({
                "Arquivo": doc["nome"], 
                "Evento": texts["events_error_default"], 
                "Data": "N/A", 
                "DataObj": None, 
                "Trecho": str(e)
            })

    # Limpa a barra de progresso após o processamento
    barra.empty()
    return eventos
