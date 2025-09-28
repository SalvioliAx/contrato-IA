import streamlit as st
import fitz  # PyMuPDF
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

@st.cache_data(show_spinner="Gerando resumo executivo...")
def gerar_resumo_executivo(arquivo_pdf_bytes, nome_arquivo_original, google_api_key):
    """
    Extrai o texto de um PDF (em bytes) e gera um resumo executivo.
    """
    if not arquivo_pdf_bytes or not google_api_key:
        return "Erro: Arquivo não fornecido ou chave da API ausente."

    texto = ""
    try:
        # Usa PyMuPDF para extrair texto do PDF em memória
        with fitz.open(stream=arquivo_pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                texto += page.get_text() + "\n"
    except Exception as e:
        return f"Erro ao extrair texto do PDF '{nome_arquivo_original}': {e}"

    if not texto.strip():
        return f"Não foi possível extrair conteúdo de texto do arquivo '{nome_arquivo_original}'."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
    prompt = PromptTemplate.from_template(
        "Crie um resumo executivo em 5 a 7 tópicos (bullet points) para o contrato abaixo. "
        "Destaque: partes, objeto, prazo, valores e condições de rescisão.\n\n"
        "Texto do Contrato:\n{texto_contrato}\n\n"
        "RESUMO EXECUTIVO:"
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        # Limita o tamanho do texto enviado à API
        res = chain.invoke({"texto_contrato": texto[:30000]})
        return res['text']
    except Exception as e:
        return f"Erro ao gerar resumo com a IA: {e}"
