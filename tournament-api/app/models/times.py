from sqlalchemy import String, Integer, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class time(Base):
    __tablename__ = "times"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    qtdjogadores: Mapped[int] = mapped_column(Integer, nullable=False)
    fase: Mapped[str] = mapped_column(String(20), nullable=False)
    contato: Mapped[str] = mapped_column(String(100), nullable=False)
