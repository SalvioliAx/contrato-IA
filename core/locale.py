# Dicionário central para todos os textos da UI e prompts da IA.
from typing import Dict, Any
import streamlit as st

# Dicionário central para todos os textos da UI e prompts da IA.
# A estrutura do dicionário foi corrigida para ser sintaticamente válida em Python.
TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "pt": {
        # Geral
        "lang_selector_label": "Idioma",
        "app_title": "ContratIA",
        "app_title_icon": "💡 ContratIA",
        "error_api_key": "Chave de API do Google ou o modelo de Embeddings não estão configurados. Verifique a barra lateral.",
        "info_load_docs": "👈 Por favor, carregue e processe documentos PDF ou uma coleção existente na barra lateral para começar.",
        # Spinners de Carregamento
        "spinner_generating_summary": "Gerando resumo...",
        "spinner_analyzing_riscos": "Analisando riscos...",
        "spinner_extracting_deadlines": "Extraindo prazos e eventos...",
        "spinner_checking_compliance": "Verificando conformidade...",
        "sidebar_spinner_processing": "Analisando documentos...",
        "dashboard_spinner_generating": "IA está analisando e gerando o dashboard...",
        # Abas
        "tab_chat": "💬 Chat",
        "tab_dashboard": "📊 Dashboard",
        "tab_summary": "📝 Resumo",
        "tab_risks": "⚠️ Riscos",
        "tab_deadlines": "⏳ Prazos",
        "tab_compliance": "✅ Conformidade",
        "tab_anomalies": "🔎 Anomalias",
        # Sidebar
        "sidebar_header": "📂 Gerenciador de Documentos",
        "sidebar_uploader_label": "Carregar novos contratos (PDF)",
        "sidebar_process_button": "Processar Documentos",
        "sidebar_save_collection_label": "Salvar Coleção Atual",
        "sidebar_save_collection_placeholder": "Nome da Coleção",
        "sidebar_save_collection_button": "Salvar",
        "sidebar_save_collection_warning": "Carregue e processe documentos primeiro para poder salvar.",
        "sidebar_load_collection_label": "Carregar Coleção Salva",
        "sidebar_load_collection_placeholder": "Selecione uma coleção",
        "sidebar_load_collection_button": "Carregar",
        # Chat
        "chat_header": "Chat de Perguntas e Respostas sobre Contratos",
        "chat_info_load_docs": "Carregue e processe documentos na barra lateral para começar a conversar.",
        "chat_welcome_message": "Olá! Sou a ContratIA. Faça-me perguntas sobre os documentos que você carregou.",
        "chat_input_placeholder": "Faça sua pergunta sobre os contratos...",
        "chat_spinner_thinking": "Pensando na resposta...",
        "chat_expander_sources": "Fontes",
        "chat_source_label": "Arquivo:",
        "chat_page_label": "Pág.",
        "chat_prompt": (
            "Você é um assistente de IA especialista em análise de contratos. "
            "Sua tarefa é responder à 'query' com base nos 'contextos' fornecidos, "
            "escrevendo a resposta final em {language}. "
            "Se não encontrar a resposta nos documentos, diga educadamente que não tem a informação. "
            "Contextos: {contextos}\nQuery: {query}\nResposta:"
        ),
        # Dashboard
        "dashboard_header": "Dashboard Dinâmico de Extração de Dados",
        "dashboard_markdown": "Utilize a IA para identificar pontos-chave e extrair dados de todos os seus contratos para análise comparativa.",
        "dashboard_info_load_docs": "Carregue e processe documentos na barra lateral para gerar o dashboard.",
        "dashboard_button_generate": "Gerar Dashboard Dinâmico com IA",
        "dashboard_warning_no_files": "Nenhum arquivo PDF original encontrado. Por favor, carregue novos arquivos na barra lateral.",
        "dashboard_subheader_table": "Dados Extraídos",
        "dashboard_subheader_viz": "Visualização de Dados Numéricos",
        "dashboard_selectbox_metric": "Selecione a Métrica Numérica para Visualizar:",
        "dashboard_chart_axis_x": "Contrato (Arquivo Fonte)",
        "dashboard_chart_title": "Comparação de {column} por Contrato",
        # Resumo
        "summary_header": "Resumo Executivo",
        "summary_info_load_docs": "Carregue um ou mais documentos na barra lateral para gerar um resumo.",
        "summary_selectbox_label": "Escolha um contrato para resumir:",
        "summary_selectbox_placeholder": "Selecione um arquivo",
        "summary_button": "Gerar Resumo para {}",
        "summary_prompt": (
            "Crie um resumo executivo em 5 a 7 tópicos (bullet points) para o contrato abaixo. "
            "O resumo deve estar em {language}. "
            "Destaque: partes, objeto, prazo, valores e condições de rescisão."
        ),
        # Riscos
        "risks_header": "Análise de Riscos Contratuais",
        "risks_info_load_docs": "Carregue um ou mais documentos na barra lateral para iniciar a análise de riscos.",
        "risks_selectbox_label": "Escolha um contrato para análise de riscos:",
        "risks_selectbox_placeholder": "Selecione um arquivo",
        "risks_button": "Analisar Riscos para {}",
        "risks_prompt": (
            "Você é um advogado especialista em riscos contratuais. Analise o Contrato '{nome}' e identifique "
            "e detalhe os 3 a 5 principais riscos jurídicos e financeiros. "
            "Para cada risco, inclua uma **Recomendação de Mitigação** concisa. "
            "O relatório deve ser escrito em {language}."
        ),
        # Prazos (Deadlines)
        "deadlines_header": "Extração de Prazos e Eventos",
        "deadlines_markdown": "Extrai automaticamente todos os prazos, datas e eventos importantes dos contratos e os organiza em uma lista.",
        "deadlines_info_load_docs": "Carregue e processe documentos na barra lateral para extrair prazos.",
        "deadlines_button_extract": "Extrair Prazos e Eventos",
        "deadlines_subheader_table": "Prazos Encontrados",
        "deadlines_subheader_chart": "Distribuição Cronológica de Eventos",
        "deadlines_chart_x_axis": "Data do Evento",
        "deadlines_chart_y_axis": "Número de Eventos",
        "deadlines_warning_no_text": "Não foi possível extrair texto de {filename} para análise de prazos.", # Novo
        "deadlines_error_read": "Erro ao ler o arquivo {filename}: {e}", # Novo
        "deadlines_warning_no_events": "Nenhum evento ou prazo foi encontrado nos documentos.", # Novo
        # Conformidade
        "compliance_header": "Verificação de Conformidade",
        "compliance_markdown": "Compare dois contratos para verificar a conformidade em termos de cláusulas principais e termos.",
        "compliance_info_load_docs": "Carregue pelo menos dois documentos na barra lateral para começar a verificação de conformidade.",
        "compliance_selectbox_ref": "1. Escolha o Documento de Referência:",
        "compliance_selectbox_comp": "2. Escolha o Documento a Comparar:",
        "compliance_button": "Verificar Conformidade",
        "compliance_error_read": "Erro ao ler o arquivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, selecione dois documentos diferentes para a comparação.",
        # Anomalías
        "anomalies_header": "Detecção de Anomalias",
        "anomalies_markdown": "Esta aba analisa os dados extraídos do dashboard para encontrar valores atípicos.",
        "anomalies_info_run_dashboard": "Para começar, vá para a aba 'Dashboard' e clique em 'Gerar Dashboard Dinâmico com IA'.",
        "anomalias_button": "Detectar Anomalias nos Dados",
        "anomalias_subheader_results": "Resultados do Análise:",
        "anomalias_success_no_anomalies": "Não foram encontradas anomalias significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Você é um analista de dados sênior. Sua tarefa é analisar textos de contratos e identificar de 5 a 7 pontos de dados que seriam interessantes para comparar em um dashboard. Sua resposta e descrições devem ser em {language}. IMPORTANTE: Sua resposta final deve ser APENAS o objeto JSON, sem texto adicional, explicações ou formatação markdown.",
        "dynamic_analyzer_field_description": "Uma descrição legível por humanos do campo, formulada como uma pergunta em {language}, ex: 'Qual é o valor total do contrato?'.",
        # Eventos internos (events.py)
        "events_progress_analyzing": "Analisando prazos em: {filename}...",
        "events_progress_extracting": "Iniciando extração de prazos...",
        "events_warning_error": "Erro ao extrair eventos de {filename}: {e}",
        "events_error_default": "Erro na extração de eventos",
    },
    "en": {
        # General
        "lang_selector_label": "Language",
        "app_title": "ContratIA",
        "app_title_icon": "💡 ContratIA",
        "error_api_key": "Google API Key or Embeddings model are not configured. Check the sidebar.",
        "info_load_docs": "👈 Please upload and process PDF documents or an existing collection in the sidebar to start.",
        # Loading Spinners
        "spinner_generating_summary": "Generating summary...",
        "spinner_analyzing_risks": "Analyzing risks...",
        "spinner_extracting_deadlines": "Extracting deadlines and events...",
        "spinner_checking_compliance": "Checking compliance...",
        "sidebar_spinner_processing": "Analyzing documents...",
        "dashboard_spinner_generating": "AI is analyzing and generating the dashboard...",
        # Tabs
        "tab_chat": "💬 Chat",
        "tab_dashboard": "📊 Dashboard",
        "tab_summary": "📝 Summary",
        "tab_risks": "⚠️ Risks",
        "tab_deadlines": "⏳ Deadlines",
        "tab_compliance": "✅ Compliance",
        "tab_anomalies": "🔎 Anomalies",
        # Sidebar
        "sidebar_header": "📂 Document Manager",
        "sidebar_uploader_label": "Upload new contracts (PDF)",
        "sidebar_process_button": "Process Documents",
        "sidebar_save_collection_label": "Save Current Collection",
        "sidebar_save_collection_placeholder": "Collection Name",
        "sidebar_save_collection_button": "Save",
        "sidebar_save_collection_warning": "Upload and process documents first to save.",
        "sidebar_load_collection_label": "Load Saved Collection",
        "sidebar_load_collection_placeholder": "Select a collection",
        "sidebar_load_collection_button": "Load",
        # Chat
        "chat_header": "Contract Q&A Chat",
        "chat_info_load_docs": "Upload and process documents in the sidebar to start chatting.",
        "chat_welcome_message": "Hello! I'm ContratIA. Ask me questions about the documents you've uploaded.",
        "chat_input_placeholder": "Ask your question about the contracts...",
        "chat_spinner_thinking": "Thinking about the answer...",
        "chat_expander_sources": "Sources",
        "chat_source_label": "File:",
        "chat_page_label": "Page",
        "chat_prompt": (
            "You are an AI assistant specialized in contract analysis. "
            "Your task is to answer the 'query' based on the provided 'contexts', "
            "writing the final answer in {language}. "
            "If you cannot find the answer in the documents, politely state that you do not have the information. "
            "Contexts: {contextos}\nQuery: {query}\nResponse:"
        ),
        # Dashboard
        "dashboard_header": "Dynamic Data Extraction Dashboard",
        "dashboard_markdown": "Use AI to identify key points and extract data from all your contracts for comparative analysis.",
        "dashboard_info_load_docs": "Upload and process documents in the sidebar to generate the dashboard.",
        "dashboard_button_generate": "Generate Dynamic Dashboard with AI",
        "dashboard_warning_no_files": "No original PDF files found. Please upload new files in the sidebar.",
        "dashboard_subheader_table": "Extracted Data",
        "dashboard_subheader_viz": "Numeric Data Visualization",
        "dashboard_selectbox_metric": "Select the Numeric Metric to Visualize:",
        "dashboard_chart_axis_x": "Contract (Source File)",
        "dashboard_chart_title": "Comparison of {column} by Contract",
        # Summary
        "summary_header": "Executive Summary",
        "summary_info_load_docs": "Upload one or more documents in the sidebar to generate a summary.",
        "summary_selectbox_label": "Choose a contract to summarize:",
        "summary_selectbox_placeholder": "Select a file",
        "summary_button": "Generate Summary for {}",
        "summary_prompt": (
            "Create an executive summary in 5 to 7 bullet points for the contract below. "
            "The summary must be in {language}. "
            "Highlight: parties, object, term, values, and termination conditions."
        ),
        # Risks
        "risks_header": "Contractual Risk Analysis",
        "risks_info_load_docs": "Upload one or more documents in the sidebar to start the risk analysis.",
        "risks_selectbox_label": "Choose a contract for risk analysis:",
        "risks_selectbox_placeholder": "Select a file",
        "risks_button": "Analyze Risks for {}",
        "risks_prompt": (
            "You are a legal expert in contractual risks. Analyze Contract '{nome}' and identify "
            "and detail the 3 to 5 main legal and financial risks. "
            "For each risk, include a concise **Mitigation Recommendation**. "
            "The report must be written in {language}."
        ),
        # Deadlines
        "deadlines_header": "Extraction of Deadlines and Events",
        "deadlines_markdown": "Automatically extracts all important deadlines, dates, and events from contracts and organizes them in a list.",
        "deadlines_info_load_docs": "Upload and process documents in the sidebar to extract deadlines.",
        "deadlines_button_extract": "Extract Deadlines and Events",
        "deadlines_subheader_table": "Deadlines Found",
        "deadlines_subheader_chart": "Chronological Distribution of Events",
        "deadlines_chart_x_axis": "Event Date",
        "deadlines_chart_y_axis": "Number of Events",
        "deadlines_warning_no_text": "Could not extract text from {filename} for deadline analysis.",
        "deadlines_error_read": "Error reading file {filename}: {e}",
        "deadlines_warning_no_events": "No events or deadlines were found in the documents.",
        # Compliance
        "compliance_header": "Compliance Verification",
        "compliance_markdown": "Compare two contracts to check compliance in terms of main clauses and terms.",
        "compliance_info_load_docs": "Upload at least two documents in the sidebar to start the compliance check.",
        "compliance_selectbox_ref": "1. Choose the Reference Document:",
        "compliance_selectbox_comp": "2. Choose the Document to Compare:",
        "compliance_button": "Verify Compliance",
        "compliance_error_read": "Error reading file {filename}: {e}",
        "compliance_warning_same_doc": "Please select two different documents for comparison.",
        # Anomalies
        "anomalies_header": "Anomaly Detection",
        "anomalies_markdown": "This tab analyzes the data extracted from the dashboard to find outliers.",
        "anomalies_info_run_dashboard": "To start, go to the 'Dashboard' tab and click on 'Generate Dynamic Dashboard with AI'.",
        "anomalias_button": "Detect Anomalies in Data",
        "anomalias_subheader_results": "Analysis Results:",
        "anomalias_success_no_anomalies": "No significant anomalies found.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "You are a senior data analyst. Your task is to analyze contract texts and identify 5 to 7 data points that would be interesting to compare in a dashboard. Your response and descriptions must be in {language}. IMPORTANT: Your final answer must be ONLY the JSON object, with no additional text, explanations, or markdown formatting.",
        "dynamic_analyzer_field_description": "A human-readable description of the field, formulated as a question in {language}, e.g., 'What is the total value of the contract?'.",
        # Eventos internos (events.py)
        "events_progress_analyzing": "Analyzing deadlines in: {filename}...",
        "events_progress_extracting": "Starting deadline extraction...",
        "events_warning_error": "Error extracting events from {filename}: {e}",
        "events_error_default": "Error in event extraction",
    },
    "es": {
        # General
        "lang_selector_label": "Idioma",
        "app_title": "ContratIA",
        "app_title_icon": "💡 ContratIA",
        "error_api_key": "La clave de API de Google o el modelo de Embeddings no están configurados. Verifique la barra lateral.",
        "info_load_docs": "👈 Por favor, cargue y procese documentos PDF o una colección existente en la barra lateral para comenzar.",
        # Loading Spinners
        "spinner_generating_summary": "Generando resumen...",
        "spinner_analyzing_risks": "Analizando riesgos...",
        "spinner_extracting_deadlines": "Extrayendo plazos y eventos...",
        "spinner_checking_compliance": "Verificando cumplimiento...",
        "sidebar_spinner_processing": "Analizando documentos...",
        "dashboard_spinner_generating": "La IA está analizando y generando el panel de control...",
        # Tabs
        "tab_chat": "💬 Chat",
        "tab_dashboard": "📊 Dashboard",
        "tab_summary": "📝 Resumen",
        "tab_risks": "⚠️ Riesgos",
        "tab_deadlines": "⏳ Plazos",
        "tab_compliance": "✅ Conformidad",
        "tab_anomalies": "🔎 Anomalías",
        # Sidebar
        "sidebar_header": "📂 Gestor de Documentos",
        "sidebar_uploader_label": "Cargar nuevos contratos (PDF)",
        "sidebar_process_button": "Procesar Documentos",
        "sidebar_save_collection_label": "Guardar Colección Actual",
        "sidebar_save_collection_placeholder": "Nombre de la Colección",
        "sidebar_save_collection_button": "Guardar",
        "sidebar_save_collection_warning": "Primero cargue y procese documentos para poder guardar.",
        "sidebar_load_collection_label": "Cargar Colección Guardada",
        "sidebar_load_collection_placeholder": "Seleccione una colección",
        "sidebar_load_collection_button": "Cargar",
        # Chat
        "chat_header": "Chat de Preguntas y Respuestas sobre Contratos",
        "chat_info_load_docs": "Cargue y procese documentos en la barra lateral para empezar a chatear.",
        "chat_welcome_message": "¡Hola! Soy ContratIA. Házme preguntas sobre los documentos que has cargado.",
        "chat_input_placeholder": "Haga su pregunta sobre los contratos...",
        "chat_spinner_thinking": "Pensando en la respuesta...",
        "chat_expander_sources": "Fuentes",
        "chat_source_label": "Archivo:",
        "chat_page_label": "Pág.",
        "chat_prompt": (
            "Usted es un asistente de IA experto en análisis de contratos. "
            "Su tarea es responder a la 'query' basándose en los 'contextos' proporcionados, "
            "escribiendo la respuesta final en {language}. "
            "Si no encuentra la respuesta en los documentos, diga educadamente que no tiene la información. "
            "Contextos: {contextos}\nQuery: {query}\nRespuesta:"
        ),
        # Dashboard
        "dashboard_header": "Panel de Control Dinámico de Extracción de Datos",
        "dashboard_markdown": "Utilice la IA para identificar puntos clave y extraer datos de todos sus contratos para análisis comparativo.",
        "dashboard_info_load_docs": "Cargue y procese documentos en la barra lateral para generar el panel de control.",
        "dashboard_button_generate": "Generar Dashboard Dinámico con IA",
        "dashboard_warning_no_files": "No se encontraron archivos PDF originales. Por favor, cargue nuevos archivos en la barra lateral.",
        "dashboard_subheader_table": "Datos Extraídos",
        "dashboard_subheader_viz": "Visualización de Datos Numéricos",
        "dashboard_selectbox_metric": "Seleccione la Métrica Numérica para Visualizar:",
        "dashboard_chart_axis_x": "Contrato (Archivo Fuente)",
        "dashboard_chart_title": "Comparación de {column} por Contrato",
        # Summary
        "summary_header": "Resumen Ejecutivo",
        "summary_info_load_docs": "Cargue uno o más documentos en la barra lateral para generar un resumen.",
        "summary_selectbox_label": "Elija un contrato para resumir:",
        "summary_selectbox_placeholder": "Seleccione un archivo",
        "summary_button": "Generar Resumen para {}",
        "summary_prompt": (
            "Cree un resumen ejecutivo en 5 a 7 puntos (bullet points) para el contrato a continuación. "
            "El resumen debe estar en {language}. "
            "Destaque: partes, objeto, plazo, valores y condiciones de rescisión."
        ),
        # Risks
        "risks_header": "Análisis de Riesgos Contractuales",
        "risks_info_load_docs": "Cargue uno o más documentos en la barra lateral para iniciar el análisis de riesgos.",
        "risks_selectbox_label": "Elija un contrato para el análisis de riesgos:",
        "risks_selectbox_placeholder": "Seleccione un archivo",
        "risks_button": "Analizar Riesgos para {}",
        "risks_prompt": (
            "Usted es un abogado experto en riesgos contractuales. Analice el Contrato '{nome}' e identifique "
            "y detalle los 3 a 5 principales riesgos legales y financieros. "
            "Para cada riesgo, inclua una concisa **Recomendación de Mitigación**. "
            "El informe debe ser escrito en {language}."
        ),
        # Deadlines
        "deadlines_header": "Extracción de Plazos y Eventos",
        "deadlines_markdown": "Extrae automáticamente todos los plazos, fechas y eventos importantes de los contratos y los organiza en una lista.",
        "deadlines_info_load_docs": "Cargue y procese documentos en la barra lateral para extraer plazos.",
        "deadlines_button_extract": "Extraer Plazos y Eventos",
        "deadlines_subheader_table": "Plazos Encontrados",
        "deadlines_subheader_chart": "Distribución Cronológica de Eventos",
        "deadlines_chart_x_axis": "Fecha del Evento",
        "deadlines_chart_y_axis": "Número de Eventos",
        "deadlines_warning_no_text": "No se pudo extraer texto de {filename} para el análisis de plazos.",
        "deadlines_error_read": "Error al leer el archivo {filename}: {e}",
        "deadlines_warning_no_events": "No se encontraron eventos o plazos en los documentos.",
        # Conformidade
        "compliance_header": "Verificación de Conformidad",
        "compliance_markdown": "Compare dos contratos para verificar el cumplimiento en términos de cláusulas principales y términos.",
        "compliance_info_load_docs": "Cargue al menos dos documentos en la barra lateral para comenzar la verificación de conformidad.",
        "compliance_selectbox_ref": "1. Elija el Documento de Referencia:",
        "compliance_selectbox_comp": "2. Elija el Documento a Comparar:",
        "compliance_button": "Verificar Conformidad",
        "compliance_error_read": "Error al leer el archivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, seleccione dos documentos diferentes para la comparación.",
        # Anomalías
        "anomalies_header": "Detección de Anomalías",
        "anomalies_markdown": "Esta pestaña analiza los datos extraídos del dashboard para encontrar valores atípicos.",
        "anomalies_info_run_dashboard": "Para comenzar, vaya a la pestaña 'Dashboard' y haga clic en 'Generar Dashboard Dinámico con IA'.",
        "anomalias_button": "Detectar Anomalías en los Datos",
        "anomalias_subheader_results": "Resultados del Análisis:",
        "anomalias_success_no_anomalies": "No se encontraron anomalías significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Eres un analista de datos senior. Tu tarea es analizar textos de contratos e identificar de 5 a 7 puntos de datos que serían interesantes para comparar en un dashboard. Tu respuesta y descripciones deben estar en {language}. IMPORTANTE: Tu respuesta final debe ser ÚNICAMENTE el objeto JSON, sin texto adicional, explicaciones o formato markdown.",
        "dynamic_analyzer_field_description": "Una descripción legible por humanos del campo, formulada como una pregunta en {language}, ej: '¿Cuál es el valor total del contrato?'.",
        # Eventos internos (events.py)
        "events_progress_analyzing": "Analizando plazos en: {filename}...",
        "events_progress_extracting": "Iniciando extracción de plazos...",
        "events_warning_error": "Error al extraer eventos de {filename}: {e}",
        "events_error_default": "Error en la extracción de eventos",
    }
}

def get_translation(key: str) -> str:
    """
    Retorna a tradução para uma chave, usando o idioma no st.session_state ou 'pt' como fallback.
    """
    try:
        # Tenta obter o idioma do st.session_state
        lang = st.session_state.get("current_language", "pt")
    except Exception:
        # Fallback se st.session_state não estiver acessível (ex: em módulos de serviço)
        lang = "pt"
    
    # Tenta obter o dicionário para o idioma, com fallback para 'pt'
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS.get('pt', {}))
    
    # Tenta obter a tradução para a chave, com fallback para a própria chave (key)
    return lang_dict.get(key, key)
