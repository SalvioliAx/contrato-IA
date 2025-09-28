import streamlit as st
from services.compliance import verificar_conformidade_documento
import fitz  # PyMuPDF

def render_conformidade_tab(embeddings_global, google_api_key):
    """
    Renderiza a aba de Verificação de Conformidade, usando arquivos da sessão.
    """
    st.header("✅ Verificação de Conformidade")

    # MODIFICADO: Usa a lista de arquivos carregados na sessão
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")

    if not arquivos_carregados or len(arquivos_carregados) < 2:
        st.info("Carregue pelo menos dois documentos na barra lateral para realizar uma comparação.")
        return

    nomes_arquivos = [f.name for f in arquivos_carregados]
    
    col1, col2 = st.columns(2)
    with col1:
        ref_nome = st.selectbox("1. Escolha o Documento de Referência:", options=nomes_arquivos, key="ref_select", index=0)
    with col2:
        # Garante que o segundo selectbox sugira um arquivo diferente
        opcoes_doc_analise = [nome for nome in nomes_arquivos if nome != ref_nome]
        doc_nome = st.selectbox("2. Escolha o Documento a Comparar:", options=opcoes_doc_analise, key="doc_select", index=0 if opcoes_doc_analise else None)

    if ref_nome and doc_nome and ref_nome != doc_nome:
        if st.button("Verificar Conformidade", use_container_width=True):
            ref_obj = next((f for f in arquivos_carregados if f.name == ref_nome), None)
            doc_obj = next((f for f in arquivos_carregados if f.name == doc_nome), None)

            if ref_obj and doc_obj:
                # Função auxiliar para extrair texto
                def extrair_texto(arquivo_obj):
                    try:
                        arquivo_obj.seek(0) # Garante a leitura desde o início
                        pdf_bytes = arquivo_obj.read()
                        texto = ""
                        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                            for page in doc:
                                texto += page.get_text() + "\n"
                        return texto
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo {arquivo_obj.name}: {e}")
                        return ""
                
                ref_text = extrair_texto(ref_obj)
                doc_text = extrair_texto(doc_obj)
                
                if ref_text and doc_text:
                    relatorio = verificar_conformidade_documento(ref_text, ref_nome, doc_text, doc_nome, google_api_key)
                    st.markdown(relatorio)
    elif ref_nome and doc_nome and ref_nome == doc_nome:
        st.warning("Por favor, selecione dois documentos diferentes para a comparação.")
