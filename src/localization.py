import json
from pathlib import Path
import streamlit as st

class Localization:
    """
    Classe para gerenciar os textos e traduções da aplicação.
    """
    def __init__(self, default_lang: str = "pt"):
        # CORREÇÃO: Usa o diretório de trabalho atual (cwd) como base,
        # que no Streamlit Cloud geralmente é a raiz do repositório.
        # Isso é mais confiável do que basear-se no caminho do ficheiro.
        base_path = Path.cwd()
        self.locales_dir = base_path / "locales"
        
        self.languages = self._load_languages()
        self.current_language = default_lang
        self.translations = self.languages.get(self.current_language, {})

        if not self.languages:
            st.warning(f"Pasta de traduções 'locales' não encontrada no caminho: {self.locales_dir}. A interface pode não ser traduzida.")

    def _load_languages(self) -> dict:
        """Carrega todos os ficheiros de tradução .json do diretório de locales."""
        langs = {}
        if not self.locales_dir.exists():
            return langs 

        for file_path in self.locales_dir.glob("*.json"):
            lang_code = file_path.stem
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    langs[lang_code] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading language file {file_path}: {e}")
        return langs

    def set_language(self, lang_code: str):
        """Define o idioma atual e carrega as traduções correspondentes."""
        if lang_code in self.languages:
            self.current_language = lang_code
            self.translations = self.languages[lang_code]
        else:
            self.current_language = "pt"
            self.translations = self.languages.get("pt", {})

    def get_translator(self):
        """
        Retorna uma função 't' que busca uma tradução por chave.
        """
        def translate(key: str, **kwargs):
            keys = key.split('.')
            value = self.translations
            try:
                for k in keys:
                    value = value[k]
                if kwargs and isinstance(value, str):
                    return value.format(**kwargs)
                return value
            except (KeyError, TypeError):
                return key
        return translate

