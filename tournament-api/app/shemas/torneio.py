from pydantic import BaseModel, ConfigDit, Field


class TorneioBase(BaseModel):
    nome: str = Field(min_length=3, max_length=50)
    modalidade: str = Field(min_length=3, max_length=30)
    descricao: str | None = Field(default=None, max_length=100)
    status: str = "aberto"


class CriarTorneio(TorneioBase):
    pass


class AtualizarTorneio(TorneioBase):
    nome: str = Field(default=None, min_length=3, max_length=50)
    modalidade: str = Field(default=None, min_length=3, max_length=30)
    descricao: str | None = Field(default=None, max_length=100)
    status: str | None = None


class RespostTorneio(TorneioBase):
    id: int

    model_config = ConfigDit(from_attributes=True)
