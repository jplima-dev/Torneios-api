from pydantic import BaseModel, ConfigDict, Field


class FaseBase(BaseModel):
    torneio_id: int = Field(gt=0)
    nome: str = Field(min_length=1, max_length=50)
    ordem: int = Field(gt=0)

class CriarFase(FaseBase):
    pass

class AtualizarFase(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    ordem: int = Field(gt=0)
    

class RespostaFase(FaseBase):
    id: int
    torneio_id: int
    nome: str
    ordem: int


    model_config = ConfigDict(from_attributes=True)