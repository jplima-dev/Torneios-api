from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Fase(Base):
    __tabelname__ = "Fase"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    torneio_id: Mapped[int] = mapped_column(ForeignKey("torneio.id"))

    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    ordem: Mapped[int] = mapped_column(nullable=False)

    