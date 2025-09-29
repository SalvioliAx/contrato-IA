import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from core.locale import TRANSLATIONS

class PontoChave(BaseModel):
    campo: str = Field(description="O nome do campo em formato snake_case, ex: 'valor_total_contrato'.")
    descricao: str = Field(description="A descrição humanamente legível do campo, formulada como uma pergunta.")

class ListaPontosChave(BaseModel):
    pontos_chave: List[PontoChave]

@st.cache_data
def identificar_pontos_chave_dinamicos(textos_contratos: str, google_api_key: str, lang_code: str):
    if not textos_contratos or not google_api_key:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
    
    # Atualiza a descrição do Pydantic dinamicamente com base no idioma
    PontoChave.model_fields['descricao'].description = TRANSLATIONS[lang_code]['dynamic_analyzer_field_description'].format(language=TRANSLATIONS[lang_code]["lang_selector_label"])
    
    parser = PydanticOutputParser(pydantic_object=ListaPontosChave)
    
    # Adiciona o OutputFixingParser como uma rede de segurança
    output_fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)

    prompt = PromptTemplate(
        template=TRANSLATIONS[lang_code]['dynamic_analyzer_prompt'],
        input_variables=["textos_contratos", "language"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm

    try:
        # CORREÇÃO: Usar o nome completo do idioma (ex: "Português", "English") conforme a chave 'lang_selector_label'
        language_name = TRANSLATIONS[lang_code]["lang_selector_label"]
        resultado_bruto = chain.invoke({
            "textos_contratos": textos_contratos[:25000], 
            "language": language_name
        })
        
        # Tenta o parser normal primeiro
        try:
            resultado_parseado = parser.parse(resultado_bruto.content)
        except Exception:
            # Se falhar, usa o parser de correção
            st.warning(TRANSLATIONS[lang_code].get("warning_ai_not_json", "A resposta inicial da IA não estava em JSON. Tentando corrigir...")) # Usando .get para evitar erro se a chave não estiver no locale
            resultado_parseado = output_fixing_parser.parse(resultado_bruto.content)
            
        return resultado_parseado.pontos_chave
        
    except Exception as e:
        st.error(f"Erro ao identificar pontos chave dinâmicos: {e}")
        return []
