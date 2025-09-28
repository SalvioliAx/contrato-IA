import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def get_qa_chain(llm, vector_store, prompt_template):
    """Cria e retorna a cadeia de RetrievalQA."""
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 7}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

def process_chat_interaction(prompt, vector_store, t, idioma_selecionado):
    """Processa a interação do utilizador, executa a cadeia de QA e formata a resposta."""
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(t("chat.spinner_thinking")):
        try:
            llm_chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)
            
            # O template do prompt é obtido do ficheiro de tradução
            template_prompt_chat_str = t(f"chat.prompt_template")
            template_prompt_chat = PromptTemplate.from_template(template_prompt_chat_str)

            qa_chain = get_qa_chain(llm_chat, vector_store, template_prompt_chat)
            resultado = qa_chain.invoke({"query": prompt})
            
            resposta_bruta = resultado["result"]
            fontes = resultado["source_documents"]
            
            # Lógica de parsing para extrair os componentes da resposta
            resposta_principal = resposta_bruta
            clausula_citada = None
            sentenca_chave = None

            separador_clausula = t("chat.separator_clause")
            separador_trecho = t("chat.separator_excerpt")

            if separador_clausula in resposta_bruta:
                partes_resposta = resposta_bruta.split(separador_clausula, 1)
                resposta_principal = partes_resposta[0].strip()
                
                if len(partes_resposta) > 1:
                    partes_resto = partes_resposta[1].split(separador_trecho, 1)
                    clausula_citada = partes_resto[0].strip()
                    
                    nao_aplicavel = t("chat.not_applicable")
                    if not clausula_citada or nao_aplicavel.lower() in clausula_citada.lower():
                        clausula_citada = None
                    
                    if len(partes_resto) > 1:
                        sentenca_chave = partes_resto[1].strip()
            
            elif separador_trecho in resposta_bruta:
                partes = resposta_bruta.split(separador_trecho, 1)
                resposta_principal = partes[0].strip()
                if len(partes) > 1:
                    sentenca_chave = partes[1].strip()

            # Limpeza final da resposta principal
            prefixo_resposta = t("chat.response_prefix")
            resposta_principal = re.sub(prefixo_resposta, "", resposta_principal, flags=re.IGNORECASE).strip()

            st.session_state.messages.append({
                "role": "assistant",
                "content": resposta_principal,
                "sources": fontes,
                "sentenca_chave": sentenca_chave,
                "clausula_citada": clausula_citada
            })

        except Exception as e_chat:
            st.error(t("chat.error_qa_chain", error=e_chat))
            st.session_state.messages.append({"role": "assistant", "content": t("chat.error_processing_request")})

