import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

# Schemas Pydantic para garantir a saída estruturada da IA
class PontoChave(BaseModel):
    """Define a estrutura de um ponto de dado chave identificado pela IA."""
    campo: str = Field(description="O nome do campo em formato snake_case, ex: 'valor_total_contrato'.")
    descricao: str = Field(description="A descrição humanamente legível do campo, formulada como uma pergunta, ex: 'Qual o valor total do contrato?'.")

class ListaPontosChave(BaseModel):
    """Define a lista de pontos chave que a IA deve retornar."""
    pontos_chave: List[PontoChave] = Field(description="Uma lista de 5 a 7 pontos de dados chave identificados.")

@st.cache_data(show_spinner="IA está identificando os pontos chave para o dashboard...")
def identificar_pontos_chave_dinamicos(textos_contratos: str, google_api_key: str):
    """
    Usa um LLM para analisar uma amostra de textos de contrato e identificar os
    pontos de dados mais relevantes para um dashboard comparativo.
    """
    if not textos_contratos or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    parser = PydanticOutputParser(pydantic_object=ListaPontosChave)

    prompt = PromptTemplate(
        template=(
            "Você é um analista de dados sênior. Sua tarefa é analisar um conjunto de textos de contratos e identificar de 5 a 7 pontos de dados (numéricos ou categóricos) que seriam mais interessantes para comparar em um dashboard.\n"
            "Pense em valores, datas, nomes de partes, durações ou condições importantes que se repetem nos documentos.\n"
            "Evite extrair frases ou parágrafos longos. Foque em dados concisos e comparáveis.\n\n"
            "TEXTOS DOS CONTRATOS (amostra):\n{textos_contratos}\n\n"
            "Gere uma lista com os 5 a 7 pontos chave que você identificou.\n"
            "{format_instructions}"
        ),
        input_variables=["textos_contratos"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    try:
        # Usamos uma amostra dos textos para otimizar e não exceder o limite de tokens da API
        amostra_textos = textos_contratos[:25000]
        resultado = chain.invoke({"textos_contratos": amostra_textos})
        return resultado.pontos_chave
    except Exception as e:
        st.error(f"Erro ao identificar pontos chave dinâmicos: {e}")
        return []

