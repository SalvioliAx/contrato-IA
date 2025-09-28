import streamlit as st
from datetime import datetime

def formatar_chat_para_markdown(mensagens_chat: list, t) -> str:
    """Formata o histórico do chat para exportação em Markdown."""
    texto_formatado = f"# {t('chat.export.title')}\n\n"
    for mensagem in mensagens_chat:
        if mensagem["role"] == "user":
            texto_formatado += f"## {t('chat.export.user_title')}:\n{mensagem['content']}\n\n"
        elif mensagem["role"] == "assistant":
            texto_formatado += f"## {t('chat.export.ai_title')}:\n{mensagem['content']}\n"
            if "sources" in mensagem and mensagem["sources"]:
                texto_formatado += f"### {t('chat.export.sources_title')}:\n"
                for i, doc_fonte in enumerate(mensagem["sources"]):
                    texto_fonte_original = doc_fonte.page_content
                    # Escapar caracteres Markdown para evitar formatação indesejada
                    texto_fonte_md = texto_fonte_original.replace('_', '\\_').replace('*', '\\*').replace('`', '\\`')
                    
                    source_name = doc_fonte.metadata.get('source', 'N/A')
                    page_num = doc_fonte.metadata.get('page', 'N/A')
                    method = doc_fonte.metadata.get('method', '')
                    method_str = f" ({t('chat.export.method')}: {method})" if method else ""

                    texto_formatado += (
                        f"- **{t('chat.export.source_label', i=i+1, doc=source_name, page=page_num, method=method_str)}**:\n"
                        f"  > {texto_fonte_md[:500]}...\n\n"
                    )
            texto_formatado += "---\n\n"
    return texto_formatado

def reset_analysis_data():
    """Limpa os dados de análise armazenados no estado da sessão."""
    keys_to_reset = [
        'df_dashboard', 'resumo_gerado', 'arquivo_resumido',
        'analise_riscos_resultados', 'eventos_contratuais_df',
        'conformidade_resultados', 'anomalias_resultados',
        'messages'
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)
    # Reinicializa a primeira mensagem do assistente
    st.session_state.messages = []
