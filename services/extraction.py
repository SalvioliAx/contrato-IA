import streamlit as st
import re, time
from typing import Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.schemas import InfoContrato
from langchain.vectorstores import FAISS

@st.cache_data(show_spinner="Extraindo dados estruturados dos contratos...")
def extrair_dados_dos_contratos(_vector_store: Optional[FAISS], _nomes_arquivos: list, google_api_key: str):
    """
    Extrai informações estruturadas (schema InfoContrato) de múltiplos contratos
    usando um vector store para busca de contexto relevante.
    """
    if not _vector_store or not google_api_key or not _nomes_arquivos:
        return []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    resultados = []
    # Mapeamento de campos para perguntas que guiarão a busca
    mapa_campos = {
        "nome_banco_emissor": "Qual o banco emissor do contrato?",
        "valor_principal_numerico": "Qual o valor monetário principal do contrato?",
        "prazo_total_meses": "Qual o prazo total do contrato em meses?",
        "taxa_juros_anual_numerica": "Qual a taxa de juros anual principal?",
        "possui_clausula_rescisao_multa": "O contrato menciona multa em caso de rescisão?",
        "condicao_limite_credito": "Quais são as condições para o limite de crédito?",
        "condicao_juros_rotativo": "Quais são as condições para juros rotativos?",
        "condicao_anuidade": "Qual é a política de anuidade do contrato?",
        "condicao_cancelamento": "Quais são as condições para cancelamento do contrato?"
    }

    total_ops = len(_nomes_arquivos) * len(mapa_campos)
    op_atual = 0
    barra = st.empty()

    for nome_arquivo in _nomes_arquivos:
        dados = {"arquivo_fonte": nome_arquivo}
        # Cria um retriever que busca apenas no arquivo atual
        retriever = _vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'filter': {'source': nome_arquivo}, 'k': 5}
        )

        for campo, pergunta in mapa_campos.items():
            op_atual += 1
            barra.progress(op_atual / total_ops, text=f"Extraindo '{campo}' de {nome_arquivo}...")

            docs = retriever.get_relevant_documents(pergunta)
            contexto = "\n\n---\n\n".join([doc.page_content for doc in docs])

            prompt = PromptTemplate.from_template(
                "Contexto:\n{contexto}\n\nCom base no contexto, responda: {pergunta}\nResposta:"
            )
            chain = LLMChain(llm=llm, prompt=prompt)

            try:
                result = chain.invoke({"contexto": contexto, "pergunta": pergunta})
                resposta = result['text'].strip()

                # Pós-processamento e normalização da resposta
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
                st.warning(f"Erro no campo {campo} para {nome_arquivo}: {e}")
                dados[campo] = None
            time.sleep(1.2) # Pausa para a API

        try:
            info = InfoContrato(**dados)
            resultados.append(info.model_dump())
        except Exception:
            # Adiciona dados mesmo que a validação Pydantic falhe, para depuração
            resultados.append(dados)
    barra.empty()
    return resultados
