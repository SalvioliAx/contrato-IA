from pathlib import Path

# --- DIRETÓRIOS ---
COLECOES_DIR = Path("colecoes_ia")
COLECOES_DIR.mkdir(exist_ok=True) # Garante que o diretório exista

# --- NOMES DOS MODELOS ---
EMBEDDING_MODEL = "models/embedding-001"
GEMINI_FLASH_MODEL = "gemini-1.5-flash-latest"

# --- CONFIGURAÇÕES DA APLICAÇÃO ---
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
