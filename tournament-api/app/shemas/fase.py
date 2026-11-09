from pydantic import BaseModel, ConfigDict, Field


class CriarFase(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    ordem: int = Field(default=1, gt=0)


class RespostaFase(CriarFase):
    id: int
    torneio_id: int
    model_config = ConfigDict(from_attributes=True)
