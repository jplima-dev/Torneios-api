from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.fase import Fase
from app.models.torneio import Torneio
from app.shemas.fase import CriarFase, RespostaFase

router = APIRouter(prefix="/torneios/{torneio_id}/fases", tags=["Fases"])


@router.get("/", response_model=list[RespostaFase])
def listar_fases(torneio_id: int, db: Session = Depends(get_db)):
    if db.get(Torneio, torneio_id) is None:
        raise HTTPException(404, "Torneio não encontrado")
    return db.scalars(select(Fase).where(Fase.torneio_id == torneio_id).order_by(Fase.ordem, Fase.id)).all()


@router.post("/", response_model=RespostaFase, status_code=status.HTTP_201_CREATED)
def criar_fase(torneio_id: int, dados: CriarFase, db: Session = Depends(get_db)):
    if db.get(Torneio, torneio_id) is None:
        raise HTTPException(404, "Torneio não encontrado")
    fase = Fase(torneio_id=torneio_id, **dados.model_dump())
    db.add(fase)
    db.commit()
    db.refresh(fase)
    return fase
