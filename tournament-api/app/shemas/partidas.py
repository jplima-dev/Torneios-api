from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PartidasBase(BaseModel):
    fase_id: int = Field(gt=0)
    time1_id: int = Field(gt=0)
    time2_id: int = Field(gt=0)
    pontos1: int = Field(default=0, ge=0)
    pontos2: int = Field(default=0, ge=0)
    data_partida: datetime


class CriarPartidas(PartidasBase):
    pass


class AtualizarPartidas(BaseModel):
    fase_id: int | None = Field(default=None, gt=0)
    pontos1: int | None = Field(default=None, ge=0)
    pontos2: int | None = Field(default=None, ge=0)
    data_partida: datetime | None = None


class RespostaPartidas(PartidasBase):
    id: int
    torneio_id: int

    model_config = ConfigDict(from_attributes=True)