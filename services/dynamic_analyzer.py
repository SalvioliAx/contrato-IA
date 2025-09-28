import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from core.locale import TRANSLATIONS

class PontoChave(BaseModel):
    campo: str = Field(description="O nome do campo em formato snake_case, ex: 'valor_total_contrato'.")
    descricao: str = Field(description="A descrição humanamente legível do campo, formulada como uma pergunta.")

class ListaPontosChave(BaseModel):
    pontos_chave: List[PontoChave]

@st.cache_data(show_spinner="IA is identifying key points for the dashboard...")
def identificar_pontos_chave_dinamicos(textos_contratos: str, google_api_key: str, lang_code: str):
    if not textos_contratos or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    
    # Atualiza a descrição do Pydantic dinamicamente com base no idioma
    PontoChave.model_fields['descricao'].description = TRANSLATIONS[lang_code]['dynamic_analyzer_field_description']
    parser = PydanticOutputParser(pydantic_object=ListaPontosChave)

    prompt = PromptTemplate(
        template=TRANSLATIONS[lang_code]['dynamic_analyzer_prompt'],
        input_variables=["textos_contratos"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chain = prompt | llm | parser

    try:
        resultado = chain.invoke({"textos_contratos": textos_contratos[:25000], "language": lang_code})
        return resultado.pontos_chave
    except Exception as e:
        st.error(f"Error identifying dynamic key points: {e}")
        return []

