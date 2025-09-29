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
        "spinner_analyzing_riscos": "Analisando riscos...",
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
        "sidebar_process_button": "Processar Documentos",
        "sidebar_save_collection_label": "Nome da Nova Coleção",
        "sidebar_save_collection_placeholder": "ex: contratos_q3",
        "sidebar_save_collection_button": "Salvar Coleção Atual",
        "sidebar_save_collection_warning": "Nenhuma coleção carregada para salvar.",
        "sidebar_load_collection_label": "Carregar Coleção Existente",
        "sidebar_load_collection_placeholder": "Selecione uma coleção...",
        "sidebar_load_collection_button": "Carregar Coleção",
        # Chat
        "chat_header": "Converse com seus Documentos",
        "chat_welcome_message": "Olá! Pergunte o que quiser sobre os documentos carregados. Por exemplo: 'Quais são os principais riscos identificados?'",
        "chat_input_placeholder": "Faça uma pergunta...",
        "chat_expander_sources": "Referências do Documento:",
        "chat_source_label": "Arquivo:",
        "chat_page_label": "Pág.",
        "chat_info_load_docs": "Por favor, carregue e processe documentos na aba lateral para iniciar o chat.",
        "chat_spinner_thinking": "Pensando na resposta...",
        "chat_prompt": (
            "Você é um assistente de IA especialista em análise de contratos. "
            "Sua tarefa é responder à pergunta do usuário APENAS com base nos documentos de contexto fornecidos. "
            "Sua resposta deve ser concisa, clara e estruturada (se necessário com listas ou parágrafos) no idioma {language}. "
            "Se a resposta não puder ser encontrada nos documentos, diga 'Não foi possível encontrar a informação nos documentos fornecidos.'\n\n"
            "Pergunta: {query}"
        ),
        # Dashboard
        "dashboard_header": "Análise de Dados Dinâmica",
        "dashboard_markdown": "Extraia dados-chave de todos os documentos para uma análise comparativa e gere um dashboard dinâmico.",
        "dashboard_info_load_docs": "Por favor, carregue e processe documentos na aba lateral para gerar o dashboard.",
        "dashboard_button_generate": "Gerar Dashboard Dinâmico com IA",
        "dashboard_warning_no_files": "Por favor, carregue os arquivos PDF originais na barra lateral para extrair o texto completo.",
        "dashboard_subheader_data": "Dados Extraídos dos Contratos:",
        "dashboard_subheader_viz": "Visualização Comparativa:",
        "dashboard_selectbox_metric": "Métrica para Visualização:",
        "dashboard_chart_axis_x": "Arquivo Fonte",
        "dashboard_chart_title": "Comparação de {column} por Contrato",
        # Resumo
        "summary_header": "Resumo Executivo",
        "summary_markdown": "Gere um resumo executivo rápido para um dos documentos carregados.",
        "summary_selectbox": "Escolha o Documento para Resumir:",
        "summary_button": "Gerar Resumo Executivo",
        "summary_prompt": (
            "Você é um analista sênior de contratos. "
            "Gere um resumo executivo conciso, focado nos pontos mais importantes, "
            "riscos e obrigações do contrato. Seu resumo deve ser no idioma {language}."
        ),
        # Riscos
        "risks_header": "Análise de Riscos",
        "risks_markdown": "Obtenha uma análise detalhada dos riscos, obrigações e potenciais pontos de negociação de um contrato.",
        "risks_selectbox": "Escolha o Documento para Análise de Riscos:",
        "risks_button": "Analisar Riscos",
        "risks_prompt": (
            "Você é um advogado especialista em mitigar riscos contratuais. "
            "Analise o contrato '{nome}' e crie uma lista estruturada de 'Riscos Principais' (com trechos do contrato), "
            "'Obrigações Críticas' e 'Pontos de Negociação' que merecem atenção. "
            "Sua análise deve ser em {language}."
        ),
        # Prazos
        "deadlines_header": "Prazos e Eventos",
        "deadlines_markdown": "Extrai e lista todos os prazos, datas e eventos importantes de todos os contratos para uma visão consolidada.",
        "deadlines_button": "Extrair Prazos e Eventos",
        "deadlines_subheader_results": "Prazos e Eventos Encontrados:",
        # Conformidade
        "compliance_header": "Verificação de Conformidade",
        "compliance_markdown": "Compare dois documentos (ex: um contrato e um aditivo) para verificar o nível de conformidade e detectar discrepâncias.",
        "compliance_selectbox_ref": "1. Escolha o Documento de Referência:",
        "compliance_selectbox_comp": "2. Escolha o Documento a Comparar:",
        "compliance_button": "Verificar Conformidade",
        "compliance_error_read": "Erro ao ler o arquivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, selecione dois documentos diferentes para a comparação.",
        # Anomalies
        "anomalies_header": "Deteção de Anomalias",
        "anomalies_markdown": "Esta aba analisa os dados extraídos do dashboard para encontrar valores atípicos.",
        "anomalies_info_run_dashboard": "Para começar, vá até a aba 'Dashboard' e clique em 'Gerar Dashboard Dinâmico com IA'.",
        "anomalies_button": "Detectar Anomalias nos Dados",
        "anomalies_subheader_results": "Resultados da Análise:",
        "anomalies_success_no_anomalies": "Não foram encontradas anomalias significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Você é um analista de dados sênior. Sua tarefa é analisar textos de contratos e identificar de 5 a 7 pontos de dados que seriam interessantes para comparar em um dashboard. Sua resposta e descrições devem estar em {language}. IMPORTANTE: Sua resposta final deve ser ÚNICAMENTE o objeto JSON, sem texto adicional, explicações ou formato markdown.",
        "dynamic_analyzer_field_description": "Uma descrição legível por humanos do campo, formulada como uma pergunta em {language}, ex: 'Qual é o valor total do contrato?'.",
    },
    "en": {
        # Geral
        "lang_selector_label": "Language",
        "app_title": "ContratIA",
        "error_api_key": "Google API key or Embeddings model are not configured. Check the sidebar.",
        "info_load_docs": "👈 Please upload and process PDF documents or an existing collection in the sidebar to begin.",
        # Spinners de Carregamento
        "spinner_generating_summary": "Generating summary...",
        "spinner_analyzing_riscos": "Analyzing risks...",
        "spinner_extracting_deadlines": "Extracting deadlines and events...",
        "spinner_checking_compliance": "Checking compliance...",
        "sidebar_spinner_processing": "Analyzing documents...",
        "dashboard_spinner_generating": "AI is analyzing and generating the dashboard...",
        # Abas
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
        "sidebar_process_button": "Process Documents",
        "sidebar_save_collection_label": "New Collection Name",
        "sidebar_save_collection_placeholder": "ex: q3_contracts",
        "sidebar_save_collection_button": "Save Current Collection",
        "sidebar_save_collection_warning": "No collection loaded to save.",
        "sidebar_load_collection_label": "Load Existing Collection",
        "sidebar_load_collection_placeholder": "Select a collection...",
        "sidebar_load_collection_button": "Load Collection",
        # Chat
        "chat_header": "Chat with Your Documents",
        "chat_welcome_message": "Hello! Ask anything you want about the uploaded documents. For example: 'What are the main risks identified?'",
        "chat_input_placeholder": "Ask a question...",
        "chat_expander_sources": "Document References:",
        "chat_source_label": "File:",
        "chat_page_label": "Page",
        "chat_info_load_docs": "Please upload and process documents in the sidebar to start the chat.",
        "chat_spinner_thinking": "Thinking about the answer...",
        "chat_prompt": (
            "You are an AI assistant specializing in contract analysis. "
            "Your task is to answer the user's question ONLY based on the context documents provided. "
            "Your answer must be concise, clear, and structured (if necessary with lists or paragraphs) in the {language} language. "
            "If the answer cannot be found in the documents, say 'Could not find the information in the provided documents.'\n\n"
            "Question: {query}"
        ),
        # Dashboard
        "dashboard_header": "Dynamic Data Analysis",
        "dashboard_markdown": "Extract key data points from all documents for comparative analysis and generate a dynamic dashboard.",
        "dashboard_info_load_docs": "Please upload and process documents in the sidebar to generate the dashboard.",
        "dashboard_button_generate": "Generate Dynamic Dashboard with AI",
        "dashboard_warning_no_files": "Please upload the original PDF files in the sidebar to extract the full text.",
        "dashboard_subheader_data": "Extracted Contract Data:",
        "dashboard_subheader_viz": "Comparative Visualization:",
        "dashboard_selectbox_metric": "Metric for Visualization:",
        "dashboard_chart_axis_x": "Source File",
        "dashboard_chart_title": "Comparison of {column} by Contract",
        # Summary
        "summary_header": "Executive Summary",
        "summary_markdown": "Generate a quick executive summary for one of the uploaded documents.",
        "summary_selectbox": "Choose Document to Summarize:",
        "summary_button": "Generate Executive Summary",
        "summary_prompt": (
            "You are a senior contract analyst. "
            "Generate a concise executive summary, focusing on the most important points, "
            "risks, and obligations of the contract. Your summary must be in the {language} language."
        ),
        # Risks
        "risks_header": "Risk Analysis",
        "risks_markdown": "Get a detailed analysis of risks, obligations, and potential negotiation points of a contract.",
        "risks_selectbox": "Choose Document for Risk Analysis:",
        "risks_button": "Analyze Risks",
        "risks_prompt": (
            "You are a lawyer specializing in mitigating contractual risks. "
            "Analyze the contract '{nome}' and create a structured list of 'Key Risks' (with contract snippets), "
            "'Critical Obligations', and 'Negotiation Points' that deserve attention. "
            "Your analysis must be in the {language} language."
        ),
        # Deadlines
        "deadlines_header": "Deadlines and Events",
        "deadlines_markdown": "Extract and list all important deadlines, dates, and events from all contracts for a consolidated view.",
        "deadlines_button": "Extract Deadlines and Events",
        "deadlines_subheader_results": "Deadlines and Events Found:",
        # Compliance
        "compliance_header": "Compliance Verification",
        "compliance_markdown": "Compare two documents (e.g., a contract and an amendment) to verify the level of compliance and detect discrepancies.",
        "compliance_selectbox_ref": "1. Choose the Reference Document:",
        "compliance_selectbox_comp": "2. Choose the Document to Compare:",
        "compliance_button": "Verify Compliance",
        "compliance_error_read": "Error reading file {filename}: {e}",
        "compliance_warning_same_doc": "Please select two different documents for comparison.",
        # Anomalies
        "anomalies_header": "Anomaly Detection",
        "anomalies_markdown": "This tab analyzes the extracted dashboard data to find outliers.",
        "anomalies_info_run_dashboard": "To start, go to the 'Dashboard' tab and click on 'Generate Dynamic Dashboard with AI'.",
        "anomalies_button": "Detect Data Anomalies",
        "anomalies_subheader_results": "Analysis Results:",
        "anomalies_success_no_anomalies": "No significant anomalies were found.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "You are a senior data analyst. Your task is to analyze contract texts and identify 5 to 7 data points that would be interesting to compare in a dashboard. Your response and descriptions must be in {language}. IMPORTANT: Your final answer must be ONLY the JSON object, without additional text, explanations, or markdown formatting.",
        "dynamic_analyzer_field_description": "A human-readable description of the field, formulated as a question in {language}, e.g.: 'What is the total contract value?'.",
    },
    "es": {
        # Geral
        "lang_selector_label": "Idioma",
        "app_title": "ContratIA",
        "error_api_key": "La clave API de Google o el modelo de Embeddings no están configurados. Verifique la barra lateral.",
        "info_load_docs": "👈 Por favor, cargue y procese documentos PDF o una colección existente en la barra lateral para comenzar.",
        # Spinners de Carregamento
        "spinner_generating_summary": "Generando resumen...",
        "spinner_analyzing_riscos": "Analizando riesgos...",
        "spinner_extracting_deadlines": "Extrayendo plazos y eventos...",
        "spinner_checking_compliance": "Verificando conformidad...",
        "sidebar_spinner_processing": "Analizando documentos...",
        "dashboard_spinner_generating": "La IA está analizando y generando el dashboard...",
        # Abas
        "tab_chat": "Chat",
        "tab_dashboard": "Dashboard",
        "tab_summary": "Resumen",
        "tab_risks": "Riesgos",
        "tab_deadlines": "Plazos",
        "tab_compliance": "Conformidad",
        "tab_anomalies": "Anomalías",
        # Sidebar
        "sidebar_header": "Gestor de Documentos",
        "sidebar_uploader_label": "Cargar nuevos contratos (PDF)",
        "sidebar_process_button": "Procesar Documentos",
        "sidebar_save_collection_label": "Nombre de la Nueva Colección",
        "sidebar_save_collection_placeholder": "ej: contratos_q3",
        "sidebar_save_collection_button": "Guardar Colección Actual",
        "sidebar_save_collection_warning": "No hay colección cargada para guardar.",
        "sidebar_load_collection_label": "Cargar Colección Existente",
        "sidebar_load_collection_placeholder": "Seleccione una colección...",
        "sidebar_load_collection_button": "Cargar Colección",
        # Chat
        "chat_header": "Chatee con sus Documentos",
        "chat_welcome_message": "¡Hola! Pregunte lo que quiera sobre los documentos cargados. Por ejemplo: '¿Cuáles son los principales riesgos identificados?'",
        "chat_input_placeholder": "Haga una pregunta...",
        "chat_expander_sources": "Referencias del Documento:",
        "chat_source_label": "Archivo:",
        "chat_page_label": "Pág.",
        "chat_info_load_docs": "Por favor, cargue y procese documentos en la barra lateral para iniciar el chat.",
        "chat_spinner_thinking": "Pensando en la respuesta...",
        "chat_prompt": (
            "Usted es un asistente de IA experto en análisis de contratos. "
            "Su tarea es responder a la pregunta del usuario SOLAMENTE basándose en los documentos de contexto proporcionados. "
            "Su respuesta debe ser concisa, clara y estructurada (si es necesario con listas o párrafos) en el idioma {language}. "
            "Si la respuesta no se puede encontrar en los documentos, diga 'No fue posible encontrar la información en los documentos proporcionados.'\n\n"
            "Pregunta: {query}"
        ),
        # Dashboard
        "dashboard_header": "Análisis Dinámico de Datos",
        "dashboard_markdown": "Extraiga puntos de datos clave de todos los documentos para un análisis comparativo y genere un dashboard dinámico.",
        "dashboard_info_load_docs": "Por favor, cargue y procese documentos en la barra lateral para generar el dashboard.",
        "dashboard_button_generate": "Generar Dashboard Dinámico con IA",
        "dashboard_warning_no_files": "Por favor, cargue los archivos PDF originales en la barra lateral para extraer el texto completo.",
        "dashboard_subheader_data": "Datos Extraídos de los Contratos:",
        "dashboard_subheader_viz": "Visualización Comparativa:",
        "dashboard_selectbox_metric": "Métrica para Visualización:",
        "dashboard_chart_axis_x": "Archivo Fuente",
        "dashboard_chart_title": "Comparación de {column} por Contrato",
        # Resumo
        "summary_header": "Resumen Ejecutivo",
        "summary_markdown": "Genere un resumen ejecutivo rápido para uno de los documentos cargados.",
        "summary_selectbox": "Elija el Documento para Resumir:",
        "summary_button": "Generar Resumen Ejecutivo",
        "summary_prompt": (
            "Usted es un analista senior de contratos. "
            "Genere un resumen ejecutivo conciso, centrado en los puntos más importantes, "
            "riesgos y obligaciones del contrato. Su resumen debe ser en el idioma {language}."
        ),
        # Riesgos
        "risks_header": "Análisis de Riesgos",
        "risks_markdown": "Obtenga un análisis detallado de los riesgos, obligaciones y posibles puntos de negociación de un contrato.",
        "risks_selectbox": "Elija el Documento para el Análisis de Riesgos:",
        "risks_button": "Analizar Riesgos",
        "risks_prompt": (
            "Usted es un abogado especializado en mitigar riesgos contractuales. "
            "Analice el contrato '{nome}' y cree una lista estructurada de 'Riesgos Clave' (con extractos del contrato), "
            "'Obligaciones Críticas' y 'Puntos de Negociación' que merecen atención. "
            "Su análisis debe ser en {language}."
        ),
        # Plazos
        "deadlines_header": "Plazos y Eventos",
        "deadlines_markdown": "Extrae y lista todos los plazos, fechas y eventos importantes de todos los contratos para una vista consolidada.",
        "deadlines_button": "Extraer Plazos y Eventos",
        "deadlines_subheader_results": "Plazos y Eventos Encontrados:",
        # Conformidad
        "compliance_header": "Verificación de Conformidad",
        "compliance_markdown": "Compare dos documentos (ej: un contrato y un aditivo) para verificar el nivel de conformidad y detectar discrepancias.",
        "compliance_selectbox_ref": "1. Elija el Documento de Referencia:",
        "compliance_selectbox_comp": "2. Elija el Documento a Comparar:",
        "compliance_button": "Verificar Conformidad",
        "compliance_error_read": "Error al leer el archivo {filename}: {e}",
        "compliance_warning_same_doc": "Por favor, seleccione dos documentos diferentes para la comparación.",
        # Anomalías
        "anomalies_header": "Detección de Anomalías",
        "anomalies_markdown": "Esta pestaña analiza los datos extraídos del dashboard para encontrar valores atípicos.",
        "anomalies_info_run_dashboard": "Para comenzar, vaya a la pestaña 'Dashboard' y haga clic en 'Generar Dashboard Dinámico con IA'.",
        "anomalies_button": "Detectar Anomalías en los Datos",
        "anomalies_subheader_results": "Resultados del Análisis:",
        "anomalies_success_no_anomalies": "No se encontraron anomalías significativas.",
        # Dynamic Analyzer
        "dynamic_analyzer_prompt": "Eres un analista de datos senior. Tu tarea es analizar textos de contratos e identificar de 5 a 7 puntos de datos que serían interesantes para comparar en un dashboard. Tu respuesta y descripciones deben estar en {language}. IMPORTANTE: Tu respuesta final debe ser ÚNICAMENTE el objeto JSON, sin texto adicional, explicaciones o formato markdown.",
        "dynamic_analyzer_field_description": "Una descripción legible por humanos del campo, formulada como una pregunta en {language}, ej: '¿Cuál es el valor total del contrato?'.",
    }
}
