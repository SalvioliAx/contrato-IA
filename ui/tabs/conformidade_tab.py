import streamlit as st
from services.compliance import verificar_conformidade_documento
import fitz


def render_conformidade_tab(embeddings_global, google_api_key, texts, lang_code):
    st.header(texts["compliance_header"])

    # --------------------------------------------------
    # Verificação de PDFs carregados
    # --------------------------------------------------
    arquivos_carregados = st.session_state.get("arquivos_pdf_originais")
    if not arquivos_carregados or len(arquivos_carregados) < 2:
        st.info(texts["compliance_info_load_docs"])
        return

    nomes_arquivos = [f.name for f in arquivos_carregados]

    # --------------------------------------------------
    # Seleção dos arquivos
    # --------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        ref_nome = st.selectbox(
            texts["compliance_selectbox_ref"],
            options=nomes_arquivos,
            key="ref_select"
        )

    with col2:
        opcoes_doc_analise = [n for n in nomes_arquivos if n != ref_nome]
        doc_nome = st.selectbox(
            texts["compliance_selectbox_comp"],
            options=opcoes_doc_analise,
            key="doc_select"
        )

    if ref_nome == doc_nome:
        st.warning(texts["compliance_warning_same_doc"])
        return

    # --------------------------------------------------
    # Ação principal - Verificar conformidade
    # --------------------------------------------------
    if st.button(texts["compliance_button"], use_container_width=True):

        with st.spinner(texts["spinner_checking_compliance"]):

            ref_obj = next((f for f in arquivos_carregados if f.name == ref_nome), None)
            doc_obj = next((f for f in arquivos_carregados if f.name == doc_nome), None)

            if not ref_obj or not doc_obj:
                st.error(texts["compliance_error_file_not_found"])
                return

            # ------------------------------------------------------
            # Extração de texto do PDF (com correção de buffer)
            # ------------------------------------------------------
            def extrair_texto(arquivo_obj):
                try:
                    # LEITURA SEGURA — evita o bug de buffer limpo após a primeira leitura
                    conteudo = arquivo_obj.getvalue()

                    if not conteudo:
                        st.error(texts["compliance_error_empty"].format(filename=arquivo_obj.name))
                        return ""

                    texto = ""
                    with fitz.open(stream=conteudo, filetype="pdf") as doc:
                        for page in doc:
                            texto += page.get_text() + "\n"

                    return texto

                except Exception as e:
                    st.error(texts["compliance_error_read"].format(filename=arquivo_obj.name, e=str(e)))
                    return ""

            ref_text = extrair_texto(ref_obj)
            doc_text = extrair_texto(doc_obj)

            # ------------------------------------------------------
            # Verificar se houve falha na extração
            # ------------------------------------------------------
            if not ref_text.strip():
                st.error(texts["compliance_error_extract_ref"].format(filename=ref_nome))
                return

            if not doc_text.strip():
                st.error(texts["compliance_error_extract_doc"].format(filename=doc_nome))
                return

            # ------------------------------------------------------
            # Chamando a função de verificação de conformidade
            # ------------------------------------------------------
            try:
                relatorio = verificar_conformidade_documento(
                    ref_text, ref_nome,
                    doc_text, doc_nome,
                    google_api_key,
                    lang_code
                )

                st.markdown(relatorio)

            except Exception as e:
                st.error(texts["compliance_error_api"].format(e=str(e)))
