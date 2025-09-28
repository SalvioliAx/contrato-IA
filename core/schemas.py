from typing import Optional, List
from pydantic import BaseModel, Field

class InfoContrato(BaseModel):
    arquivo_fonte: str = Field(description="O nome do arquivo de origem do contrato.")
    nome_banco_emissor: Optional[str] = Field(default="Não encontrado")
    valor_principal_numerico: Optional[float] = None
    prazo_total_meses: Optional[int] = None
    taxa_juros_anual_numerica: Optional[float] = None
    possui_clausula_rescisao_multa: Optional[str] = Field(default="Não claro")
    condicao_limite_credito: Optional[str] = Field(default="Não encontrado")
    condicao_juros_rotativo: Optional[str] = Field(default="Não encontrado")
    condicao_anuidade: Optional[str] = Field(default="Não encontrado")
    condicao_cancelamento: Optional[str] = Field(default="Não encontrado")

class EventoContratual(BaseModel):
    descricao_evento: str
    data_evento_str: Optional[str] = "Não Especificado"
    trecho_relevante: Optional[str] = None

class ListaDeEventos(BaseModel):
    eventos: List[EventoContratual]
    arquivo_fonte: str
