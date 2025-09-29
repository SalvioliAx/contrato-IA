# Dicionário central para todos os textos da UI e prompts da IA.
TRANSLATIONS = {
    "pt": {
        # Geral
        "lang_selector_label": "Idioma",
        "app_title": "ContratIA",
        "error_api_key": "Chave de API do Google ou o modelo de Embeddings não estão configurados. Verifique a barra lateral.",
        "info_load_docs": "👈 Por favor, carregue e processe documentos PDF ou uma coleção existente na barra lateral para começar.",
        # Spinners de Carregamento
        "spinner_generating_summary": "Gerando resumo...",
        "spinner_analyzing_risks": "Analisando riscos...",
        "spinner_extracting_deadlines": "Extraindo prazos e eventos...",
        "spinner_checking_compliance": "Verificando conformidade...",
        "sidebar_spinner_processing": "Analisando documentos...",
        "dashboard_spinner_generating": "IA está analisando e gerando o dashboard...",
        # Abas
        "tab_chat": "Chat",
        "tab_dashboard": "Dashboard",
        "tab_summary": "Resumo",
        "tab_risks": "Riscos",
        "tab_deadlines": "Prazos",
        "tab_compliance": "Conformidade",
        "tab_anomalies": "Anomalias",
        # Sidebar
        "sidebar_header": "Gerenciador de Documentos",
        "sidebar_uploader_label": "Carregar novos contratos (PDF)",
        "sidebar_process_button": "Processar Documentos 🚀",
        "sidebar_save_collection_label": "Nome da Coleção a Salvar",
        "sidebar_save_collection_button": "Salvar Coleção",
        "sidebar_load_collection_label": "Carregar Coleção Existente",
        "sidebar_load_collection_button": "Carregar Selecionada",
        "sidebar_load_collection_placeholder": "Selecione uma coleção",
        "sidebar_save_collection_warning": "Carregue e processe documentos antes de salvar.",
        # Chat
        "chat_header": "Chat com o Contrato",
        "chat_info_load_docs": "Carregue e processe documentos para iniciar o chat.",
        "chat_welcome_message": "Olá! Pergunte o que quiser sobre os documentos processados.",
        "chat_input_placeholder": "Faça uma pergunta...",
        "chat_expander_sources": "Fontes Relevantes",
        "chat_source_label": "Fonte:",
        "chat_page_label": "Pág.",
        "chat_spinner_thinking": "Gemini está pensando...",
        # Dashboard
        "dashboard_header": "Dashboard Dinâmico",
        "dashboard_markdown": "Extraia dados-chave de todos os contratos e visualize-os em um dashboard comparativo.",
        "dashboard_info_load_docs": "Carregue e processe documentos para extrair os dados.",
        "dashboard_warning_no_files": "Nenhum arquivo PDF original encontrado. Por favor, carregue e processe documentos na barra lateral.",
        "dashboard_button_generate": "Gerar Dashboard Dinâmico com IA",
        "dashboard_subheader_data": "Dados Extraídos",
        "dashboard_subheader_viz": "Visualização Comparativa",
        "dashboard_selectbox_metric": "Métrica para Visualizar:",
        "dashboard_chart_axis_x": "Contrato",
        "dashboard_chart_title": "Comparação de {column} por Contrato",
        # **RESUMO (Novas Chaves Adicionadas)**
        "summary_header": "Resumo Executivo",
        "summary_info_load_docs": "Carregue e processe documentos na barra lateral para gerar um resumo.",
        "summary_selectbox_label": "1. Escolha um Contrato para Resumir:",
        "summary_selectbox_placeholder": "Selecione um arquivo",
        "summary_button": "Gerar Resumo Executivo",
        "summary_prompt": (
            "Você é um especialista em contratos. Crie um resumo executivo conciso em 5 a 7 tópicos (bullet points) "
            "para o contrato abaixo. Destaque: partes, objeto, prazo, valores e condições de rescisão. "
            "O resumo deve ser escrito em {language}."
        ),
        # Riscos
        "risks_header": "Análise de Riscos",
        "risks_markdown": "Identifique cláusulas de risco ou pontos de atenção no contrato selecionado.",
        "risks_info_load_docs": "Carregue e processe documentos na barra lateral para analisar riscos.",
        "risks_selectbox_label": "1. Escolha um Contrato para Análise de Riscos:",
        "risks_selectbox_placeholder": "Selecione um arquivo",
        "risks_button": "Analisar Riscos",
        "risks_prompt": (
            "Você é um analista de riscos sênior. Analise o contrato '{nome}' e identifique os 3 principais riscos "
            "ou cláusulas desfavoráveis, com recomendações de mitigação. Sua análise deve ser escrita em {language}. "
            "Use um formato claro com títulos em Markdown."
        ),
        # Prazos
        "deadlines_header": "Extração de Prazos e Eventos",
        "deadlines_markdown": "Visualize todos os prazos e eventos importantes extraídos dos contratos em uma linha do tempo.",
        "deadlines_info_load_docs": "Carregue e processe documentos para extrair prazos.",
        "deadlines_button": "Extrair Prazos e Eventos",
        "deadlines_subheader_results": "Resultados da Extração",
        "deadlines_subheader_calendar": "Visualização Calendário",
        "deadlines_error_no_events": "Nenhum evento ou prazo com data válida foi extraído dos documentos.",
        # Conformidade
        "compliance_header": "Verificação de Conformidade",
        "compliance_markdown": "Compare um contrato (A) com um contrato de referência (B) para verificar a conformidade de termos.",
        "compliance_info_load_docs": "Carregue e processe documentos para verificação de conformidade.",
        "compliance_selectbox_ref": "1. Escolha o Documento de Referência:",
        "compliance_selectbox_comp": "2. Escolha o Documento a Comparar:",
        "compliance_button": "Verificar Conformidade",
        "compliance_error_read": "Erro ao ler o arquivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, selecione dois documentos diferentes para a comparação.",
        # Anomalías
        "anomalies_header": "Deteção de Anomalias",
        "anomalies_markdown": "Esta aba analisa os dados extraídos do dashboard para encontrar valores atípicos.",
        "anomalias_info_run_dashboard": "Para começar, vá para a aba 'Dashboard' e clique em 'Gerar Dashboard Dinâmico com IA'.",
        "anomalias_button": "Detetar Anomalias nos Dados",
        "anomalias_subheader_results": "Resultados do Análise:",
        "anomalias_success_no_anomalies": "Não foram encontradas anomalias significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Você é um analista de dados sênior. Sua tarefa é analisar textos de contratos e identificar de 5 a 7 pontos de dados que seriam interessantes para comparar em um dashboard. Sua resposta e descrições devem ser em {language}. IMPORTANTE: Sua resposta final deve ser APENAS o objeto JSON, sem texto adicional, explicações ou formatação markdown.",
        "dynamic_analyzer_field_description": "Uma descrição legível por humanos do campo, formulada como uma pergunta em {language}, ex: 'Qual é o valor total do contrato?'.",
    },
    "en": {
        # General
        "lang_selector_label": "Language",
        "app_title": "ContratIA",
        "error_api_key": "Google API key or Embeddings model is not configured. Check the sidebar.",
        "info_load_docs": "👈 Please load and process PDF documents or an existing collection in the sidebar to start.",
        # Loading Spinners
        "spinner_generating_summary": "Generating summary...",
        "spinner_analyzing_risks": "Analyzing risks...",
        "spinner_extracting_deadlines": "Extracting deadlines and events...",
        "spinner_checking_compliance": "Checking compliance...",
        "sidebar_spinner_processing": "Analyzing documents...",
        "dashboard_spinner_generating": "AI is analyzing and generating the dashboard...",
        # Tabs
        "tab_chat": "Chat",
        "tab_dashboard": "Dashboard",
        "tab_summary": "Summary",
        "tab_risks": "Risks",
        "tab_deadlines": "Deadlines",
        "tab_compliance": "Compliance",
        "tab_anomalies": "Anomalies",
        # Sidebar
        "sidebar_header": "Document Manager",
        "sidebar_uploader_label": "Upload new contracts (PDF)",
        "sidebar_process_button": "Process Documents 🚀",
        "sidebar_save_collection_label": "Collection Name to Save",
        "sidebar_save_collection_button": "Save Collection",
        "sidebar_load_collection_label": "Load Existing Collection",
        "sidebar_load_collection_button": "Load Selected",
        "sidebar_load_collection_placeholder": "Select a collection",
        "sidebar_save_collection_warning": "Load and process documents before saving.",
        # Chat
        "chat_header": "Chat with Contract",
        "chat_info_load_docs": "Load and process documents to start the chat.",
        "chat_welcome_message": "Hello! Ask anything you want about the processed documents.",
        "chat_input_placeholder": "Ask a question...",
        "chat_expander_sources": "Relevant Sources",
        "chat_source_label": "Source:",
        "chat_page_label": "Page",
        "chat_spinner_thinking": "Gemini is thinking...",
        # Dashboard
        "dashboard_header": "Dynamic Dashboard",
        "dashboard_markdown": "Extract key data points from all contracts and visualize them in a comparative dashboard.",
        "dashboard_info_load_docs": "Load and process documents to extract data.",
        "dashboard_warning_no_files": "No original PDF files found. Please upload and process documents in the sidebar.",
        "dashboard_button_generate": "Generate Dynamic Dashboard with AI",
        "dashboard_subheader_data": "Extracted Data",
        "dashboard_subheader_viz": "Comparative Visualization",
        "dashboard_selectbox_metric": "Metric to Visualize:",
        "dashboard_chart_axis_x": "Contract",
        "dashboard_chart_title": "Comparison of {column} by Contract",
        # **SUMMARY (New Keys Added)**
        "summary_header": "Executive Summary",
        "summary_info_load_docs": "Load and process documents in the sidebar to generate a summary.",
        "summary_selectbox_label": "1. Select a Contract to Summarize:",
        "summary_selectbox_placeholder": "Select a file",
        "summary_button": "Generate Executive Summary",
        "summary_prompt": (
            "You are a contract expert. Create a concise executive summary in 5 to 7 bullet points "
            "for the contract below. Highlight: parties, object, term, values, and termination conditions. "
            "The summary must be written in {language}."
        ),
        # Risks
        "risks_header": "Risk Analysis",
        "risks_markdown": "Identify risk clauses or attention points in the selected contract.",
        "risks_info_load_docs": "Load and process documents in the sidebar to analyze risks.",
        "risks_selectbox_label": "1. Select a Contract for Risk Analysis:",
        "risks_selectbox_placeholder": "Select a file",
        "risks_button": "Analyze Risks",
        "risks_prompt": (
            "You are a senior risk analyst. Analyze the contract '{nome}' and identify the 3 main risks "
            "or unfavorable clauses, with mitigation recommendations. Your analysis must be written in {language}. "
            "Use a clear format with Markdown headings."
        ),
        # Deadlines
        "deadlines_header": "Deadline and Event Extraction",
        "deadlines_markdown": "View all important deadlines and events extracted from contracts in a timeline.",
        "deadlines_info_load_docs": "Load and process documents to extract deadlines.",
        "deadlines_button": "Extract Deadlines and Events",
        "deadlines_subheader_results": "Extraction Results",
        "deadlines_subheader_calendar": "Calendar View",
        "deadlines_error_no_events": "No events or deadlines with a valid date were extracted from the documents.",
        # Compliance
        "compliance_header": "Compliance Verification",
        "compliance_markdown": "Compare one contract (A) with a reference contract (B) to verify term compliance.",
        "compliance_info_load_docs": "Load and process documents for compliance verification.",
        "compliance_selectbox_ref": "1. Select the Reference Document:",
        "compliance_selectbox_comp": "2. Select the Document to Compare:",
        "compliance_button": "Verify Compliance",
        "compliance_error_read": "Error reading file {filename}: {e}",
        "compliance_warning_same_doc": "Please select two different documents for comparison.",
        # Anomalies
        "anomalies_header": "Anomaly Detection",
        "anomalies_markdown": "This tab analyzes the data extracted from the dashboard to find outliers.",
        "anomalias_info_run_dashboard": "To start, go to the 'Dashboard' tab and click 'Generate Dynamic Dashboard with AI'.",
        "anomalias_button": "Detect Anomalies in Data",
        "anomalias_subheader_results": "Analysis Results:",
        "anomalias_success_no_anomalies": "No significant anomalies were found.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "You are a senior data analyst. Your task is to analyze contract texts and identify 5 to 7 data points that would be interesting to compare in a dashboard. Your response and descriptions must be in {language}. IMPORTANT: Your final response must be ONLY the JSON object, without additional text, explanations, or markdown formatting.",
        "dynamic_analyzer_field_description": "A human-readable description of the field, formulated as a question in {language}, e.g.: 'What is the total contract value?'.",
    },
    "es": {
        # General
        "lang_selector_label": "Idioma",
        "app_title": "ContratIA",
        "error_api_key": "La clave API de Google o el modelo de Embeddings no están configurados. Verifique la barra lateral.",
        "info_load_docs": "👈 Por favor, cargue y procese documentos PDF o una colección existente en la barra lateral para empezar.",
        # Loading Spinners
        "spinner_generating_summary": "Generando resumen...",
        "spinner_analyzing_risks": "Analizando riesgos...",
        "spinner_extracting_deadlines": "Extrayendo plazos y eventos...",
        "spinner_checking_compliance": "Verificando cumplimiento...",
        "sidebar_spinner_processing": "Analizando documentos...",
        "dashboard_spinner_generating": "La IA está analizando y generando el panel...",
        # Tabs
        "tab_chat": "Chat",
        "tab_dashboard": "Panel de Control",
        "tab_summary": "Resumen",
        "tab_risks": "Riesgos",
        "tab_deadlines": "Plazos",
        "tab_compliance": "Cumplimiento",
        "tab_anomalies": "Anomalías",
        # Sidebar
        "sidebar_header": "Administrador de Documentos",
        "sidebar_uploader_label": "Cargar nuevos contratos (PDF)",
        "sidebar_process_button": "Procesar Documentos 🚀",
        "sidebar_save_collection_label": "Nombre de la Colección a Guardar",
        "sidebar_save_collection_button": "Guardar Colección",
        "sidebar_load_collection_label": "Cargar Colección Existente",
        "sidebar_load_collection_button": "Cargar Seleccionada",
        "sidebar_load_collection_placeholder": "Seleccione una colección",
        "sidebar_save_collection_warning": "Cargue y procese documentos antes de guardar.",
        # Chat
        "chat_header": "Chat con el Contrato",
        "chat_info_load_docs": "Cargue y procese documentos para iniciar el chat.",
        "chat_welcome_message": "¡Hola! Pregunte lo que quiera sobre los documentos procesados.",
        "chat_input_placeholder": "Haga una pregunta...",
        "chat_expander_sources": "Fuentes Relevantes",
        "chat_source_label": "Fuente:",
        "chat_page_label": "Pág.",
        "chat_spinner_thinking": "Gemini está pensando...",
        # Dashboard
        "dashboard_header": "Panel de Control Dinámico",
        "dashboard_markdown": "Extraiga puntos de datos clave de todos los contratos y visualícelos en un panel de control comparativo.",
        "dashboard_info_load_docs": "Cargue y procese documentos para extraer los datos.",
        "dashboard_warning_no_files": "No se encontraron archivos PDF originales. Por favor, cargue y procese documentos en la barra lateral.",
        "dashboard_button_generate": "Generar Panel de Control Dinámico con IA",
        "dashboard_subheader_data": "Datos Extraídos",
        "dashboard_subheader_viz": "Visualización Comparativa",
        "dashboard_selectbox_metric": "Métrica para Visualizar:",
        "dashboard_chart_axis_x": "Contrato",
        "dashboard_chart_title": "Comparación de {column} por Contrato",
        # **RESUMEN (Nuevas Claves Adicionadas)**
        "summary_header": "Resumen Ejecutivo",
        "summary_info_load_docs": "Cargue y procese documentos en la barra lateral para generar un resumen.",
        "summary_selectbox_label": "1. Seleccione un Contrato para Resumir:",
        "summary_selectbox_placeholder": "Seleccione un archivo",
        "summary_button": "Generar Resumen Ejecutivo",
        "summary_prompt": (
            "Usted es un experto en contratos. Cree un resumen ejecutivo conciso en 5 a 7 puntos clave (bullet points) "
            "para el contrato a continuación. Destaque: partes, objeto, plazo, valores y condiciones de rescisión. "
            "El resumen debe ser escrito en {language}."
        ),
        # Risks
        "risks_header": "Análisis de Riesgos",
        "risks_markdown": "Identifique cláusulas de riesgo o puntos de atención en el contrato seleccionado.",
        "risks_info_load_docs": "Cargue y procese documentos en la barra lateral para analizar riesgos.",
        "risks_selectbox_label": "1. Seleccione un Contrato para Análisis de Riesgos:",
        "risks_selectbox_placeholder": "Seleccione un archivo",
        "risks_button": "Analizar Riesgos",
        "risks_prompt": (
            "Usted es un analista de riesgos senior. Analice el contrato '{nome}' e identifique los 3 principales riesgos "
            "o cláusulas desfavorables, con recomendaciones de mitigación. Su análisis debe ser escrito en {language}. "
            "Utilice un formato claro con títulos en Markdown."
        ),
        # Deadlines
        "deadlines_header": "Extracción de Plazos y Eventos",
        "deadlines_markdown": "Vea todos los plazos y eventos importantes extraídos de los contratos en una línea de tiempo.",
        "deadlines_info_load_docs": "Cargue y procese documentos para extraer plazos.",
        "deadlines_button": "Extraer Plazos y Eventos",
        "deadlines_subheader_results": "Resultados de la Extracción",
        "deadlines_subheader_calendar": "Visualización de Calendario",
        "deadlines_error_no_events": "No se extrajeron eventos o plazos con fecha válida de los documentos.",
        # Compliance
        "compliance_header": "Verificación de Cumplimiento",
        "compliance_markdown": "Compare un contrato (A) con un contrato de referencia (B) para verificar el cumplimiento de términos.",
        "compliance_info_load_docs": "Cargue y procese documentos para verificación de cumplimiento.",
        "compliance_selectbox_ref": "1. Elija el Documento de Referencia:",
        "compliance_selectbox_comp": "2. Elija el Documento a Comparar:",
        "compliance_button": "Verificar Conformidad",
        "compliance_error_read": "Error al leer el archivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, seleccione dos documentos diferentes para la comparación.",
        # Anomalías
        "anomalies_header": "Detección de Anomalías",
        "anomalies_markdown": "Esta pestaña analiza los datos extraídos del panel de control para encontrar valores atípicos.",
        "anomalias_info_run_dashboard": "Para comenzar, vaya a la pestaña 'Panel de Control' y haga clic en 'Generar Panel de Control Dinámico con IA'.",
        "anomalias_button": "Detectar Anomalías en los Datos",
        "anomalias_subheader_results": "Resultados del Análisis:",
        "anomalias_success_no_anomalies": "No se encontraron anomalías significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Eres un analista de datos senior. Tu tarea es analizar textos de contratos e identificar de 5 a 7 puntos de datos que serían interesantes para comparar en un panel de control. Tu respuesta y descripciones deben estar en {language}. IMPORTANTE: Tu respuesta final debe ser ÚNICAMENTE el objeto JSON, sin texto adicional, explicaciones o formato markdown.",
        "dynamic_analyzer_field_description": "Una descripción legible por humanos del campo, formulada como una pregunta en {language}, ej: '¿Cuál es el valor total del contrato?'.",
    }
}
