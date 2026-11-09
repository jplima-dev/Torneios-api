from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.times import Times
from app.models.torneio import Torneio
from app.shemas.times import AtualizarTimes, CriarTimes, RespostaTimes

router = APIRouter(prefix="/torneios/{torneio_id}/times", tags=["Times"])


def obter_time(torneio_id: int, time_id: int, db: Session) -> Times:
    time = db.get(Times, time_id)
    if time is None or time.torneio_id != torneio_id:
        raise HTTPException(404, "Time não encontrado")
    return time


@router.get("/", response_model=list[RespostaTimes])
def listar_times(torneio_id: int, db: Session = Depends(get_db)):
    if db.get(Torneio, torneio_id) is None:
        raise HTTPException(404, "Torneio não encontrado")
    return db.scalars(select(Times).where(Times.torneio_id == torneio_id).order_by(Times.id)).all()


@router.post("/", response_model=RespostaTimes, status_code=status.HTTP_201_CREATED)
def criar_time(torneio_id: int, dados: CriarTimes, db: Session = Depends(get_db)):
    if db.get(Torneio, torneio_id) is None:
        raise HTTPException(404, "Torneio não encontrado")
    time = Times(torneio_id=torneio_id, **dados.model_dump())
    db.add(time)
    db.commit()
    db.refresh(time)
    return time


@router.get("/{time_id}", response_model=RespostaTimes)
def buscar_time(torneio_id: int, time_id: int, db: Session = Depends(get_db)):
    return obter_time(torneio_id, time_id, db)


@router.put("/{time_id}", response_model=RespostaTimes)
def atualizar_time(torneio_id: int, time_id: int, dados: AtualizarTimes, db: Session = Depends(get_db)):
    time = obter_time(torneio_id, time_id, db)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(time, campo, valor)
    db.commit()
    db.refresh(time)
    return time


@router.delete("/{time_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_time(torneio_id: int, time_id: int, db: Session = Depends(get_db)):
    db.delete(obter_time(torneio_id, time_id, db))
    db.commit()
