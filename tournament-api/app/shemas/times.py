from pydantic import BaseModel, ConfigDict, Field


class TimesBase(BaseModel):
    nome: str = Field(min_length=3, max_length=50)
    qtdjogadores: int = Field(default=3, ge=3)
    contato: str = Field(max_length=100)


class CriarTimes(TimesBase):
    pass


class AtualizarTimes(BaseModel):
    nome: str = Field(default=None, min_length=3, max_length=50)
    qtdjogadores: int = Field(default=3, ge=3)
    contato: str | None = Field(max_Length=100)


class RespostaTimes(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
