from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Partida(Base):
    __tablename__ = "partidas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    torneio_id: Mapped[int] = mapped_column(ForeignKey("torneio.id"), nullable=False)
    fase_id: Mapped[int] = mapped_column(ForeignKey("fases.id"), nullable=False)

    time1_id: Mapped[int] = mapped_column(ForeignKey("times.id"), nullable=False)
    time2_id: Mapped[int] = mapped_column(ForeignKey("times.id"), nullable=False)

    pontos1: Mapped[int] = mapped_column(Integer, default=0)
    pontos2: Mapped[int] = mapped_column(Integer, default=0)

    data_partida: Mapped[datetime] = mapped_column(DateTime, nullable=False)
