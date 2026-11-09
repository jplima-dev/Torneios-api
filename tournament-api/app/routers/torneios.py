from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.torneio import Torneio
from app.shemas.torneio import AtualizarTorneio, CriarTorneio, RespostaTorneio

router = APIRouter(prefix="/torneios", tags=["Torneios"])


@router.get("/", response_model=list[RespostaTorneio])
def listar_torneios(db: Session = Depends(get_db)):
    return db.scalars(select(Torneio).order_by(Torneio.id.desc())).all()


@router.post("/", response_model=RespostaTorneio, status_code=status.HTTP_201_CREATED)
def criar_torneio(dados: CriarTorneio, db: Session = Depends(get_db)):
    torneio = Torneio(**dados.model_dump())
    db.add(torneio)
    db.commit()
    db.refresh(torneio)
    return torneio


@router.get("/{torneio_id}", response_model=RespostaTorneio)
def buscar_torneio(torneio_id: int, db: Session = Depends(get_db)):
    torneio = db.get(Torneio, torneio_id)
    if torneio is None:
        raise HTTPException(404, "Torneio não encontrado")
    return torneio


@router.put("/{torneio_id}", response_model=RespostaTorneio)
def atualizar_torneio(torneio_id: int, dados: AtualizarTorneio, db: Session = Depends(get_db)):
    torneio = buscar_torneio(torneio_id, db)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(torneio, campo, valor)
    db.commit()
    db.refresh(torneio)
    return torneio


@router.delete("/{torneio_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_torneio(torneio_id: int, db: Session = Depends(get_db)):
    db.delete(buscar_torneio(torneio_id, db))
    db.commit()
