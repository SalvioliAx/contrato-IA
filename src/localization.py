import json
from pathlib import Path

class Localization:
    """
    Classe para gerenciar os textos e traduções da aplicação.
    """
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.languages = self._load_languages()
        self.current_language = "pt"  # Idioma padrão
        self.translations = self.languages.get(self.current_language, {})

    def _load_languages(self) -> dict:
        """Carrega todos os ficheiros de tradução .json do diretório de locales."""
        langs = {}
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
            print(f"Language '{lang_code}' not found. Defaulting to 'pt'.")
            self.current_language = "pt"
            self.translations = self.languages.get("pt", {})

    def get_translator(self):
        """
        Retorna uma função 't' que busca uma tradução por chave.
        Exemplo de uso: t("sidebar.title")
        """
        def translate(key: str, **kwargs):
            """
            Busca a tradução para uma chave. Suporta chaves aninhadas (ex: "sidebar.title").
            Permite a formatação de strings com argumentos.
            """
            keys = key.split('.')
            value = self.translations
            try:
                for k in keys:
                    value = value[k]
                if kwargs:
                    return value.format(**kwargs)
                return value
            except KeyError:
                # Retorna a própria chave se a tradução não for encontrada
                return key
        return translate

