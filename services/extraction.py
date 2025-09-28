import streamlit as st
import re, time
from typing import Optional
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.schemas import InfoContrato
from langchain.vectorstores import FAISS

@st.cache_data(show_spinner="Extraindo dados dos contratos...")
def extrair_dados_dos_contratos(_vector_store: Optional[FAISS], _nomes_arquivos: list, google_api_key: str):
    if not _vector_store or not google_api_key or not _nomes_arquivos:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

    resultados = []
    mapa_campos = {
        "nome_banco_emissor": "Qual o banco emissor do contrato?",
        "valor_principal_numerico": "Qual o valor monetário principal?",
        "prazo_total_meses": "Qual o prazo total em meses?",
        "taxa_juros_anual_numerica": "Qual a taxa de juros anual?",
        "possui_clausula_rescisao_multa": "Existe cláusula de multa em caso de rescisão?",
        "condicao_limite_credito": "Quais condições definem o limite de crédito?",
        "condicao_juros_rotativo": "Quais condições aplicam juros rotativos?",
        "condicao_anuidade": "Qual a política de cobrança de anuidade?",
        "condicao_cancelamento": "Quais condições de cancelamento existem?"
    }

    total = len(_nomes_arquivos) * len(mapa_campos)
    atual = 0
    barra = st.empty()

    for nome_arquivo in _nomes_arquivos:
        dados = {"arquivo_fonte": nome_arquivo}
        retriever = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )

        for campo, pergunta in mapa_campos.items():
            atual += 1
            barra.progress(atual / total, text=f"Extraindo {campo} de {nome_arquivo}...")

            docs = retriever.get_relevant_documents(pergunta)
            contexto = "\n".join([doc.page_content for doc in docs])

            prompt = PromptTemplate.from_template(
                "Contexto:\n{contexto}\n\nPergunta: {pergunta}\nResposta:"
            )
            chain = LLMChain(llm=llm, prompt=prompt)

            try:
                result = chain.invoke({"contexto": contexto, "pergunta": pergunta})
                resposta = result['text'].strip()

                # Normalizar numéricos
                if campo in ["valor_principal_numerico", "prazo_total_meses", "taxa_juros_anual_numerica"]:
                    numeros = re.findall(r"[\d]+(?:[.,]\d+)*", resposta)
                    if numeros:
                        val = numeros[0].replace('.', '').replace(',', '.')
                        try:
                            dados[campo] = float(val) if campo != "prazo_total_meses" else int(float(val))
                        except ValueError:
                            dados[campo] = None
                else:
                    dados[campo] = resposta
            except Exception as e:
                st.warning(f"Erro no campo {campo}: {e}")
                dados[campo] = None

            time.sleep(1.2)

        try:
            info = InfoContrato(**dados)
            resultados.append(info.model_dump())
        except Exception:
            resultados.append(dados)

    barra.empty()
    return resultados
