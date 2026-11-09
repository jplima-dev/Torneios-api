from pydantic import BaseModel, ConfigDict, Field


class TorneioBase(BaseModel):
    nome: str = Field(min_length=3, max_length=50)
    modalidade: str = Field(min_length=3, max_length=30)
    descricao: str | None = Field(default=None, max_length=100)
    status: str = "aberto"


class CriarTorneio(TorneioBase):
    pass


class AtualizarTorneio(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=50)
    modalidade: str | None = Field(default=None, min_length=3, max_length=30)
    descricao: str | None = Field(default=None, max_length=100)
    status: str | None = None


class RespostaTorneio(TorneioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
