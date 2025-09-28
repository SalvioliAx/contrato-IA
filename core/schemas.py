from typing import Optional, List
from pydantic import BaseModel, Field

# A classe InfoContrato foi removida pois não é mais utilizada pela extração dinâmica.

class EventoContratual(BaseModel):
    """
    Schema para um único evento ou prazo extraído de um contrato.
    Utilizado pela aba 'Prazos'.
    """
    descricao_evento: str
    data_evento_str: Optional[str] = "Não Especificado"
    trecho_relevante: Optional[str] = None

class ListaDeEventos(BaseModel):
    """
    Schema para uma lista de eventos contratuais de um arquivo fonte.
    Utilizado pela aba 'Prazos'.
    """
    eventos: List[EventoContratual]
    arquivo_fonte: str

