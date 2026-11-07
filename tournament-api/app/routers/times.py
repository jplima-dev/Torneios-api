from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.times import Time
from app.models.torneio import Torneio
from app.shemas.times import (
    AtualizarTimes,
    CriarTimes,
    RespostaTimes,
)

# from app.shemas.fase import

router = APIRouter(prefix="/torneios/{torneios.id}/partidas", tags=["Times"])

@router.post("/", reponse_model=RespostaTimes, status_code=status.HTTP_201_CREATED)
def criar_times(dados: CriarTimes, db: Session = Depends(get_db)):
    novo_time = Time(**db.model_dump())

    try:
        db.add(novo_time)
        db.commit()
        db.refresh(novo_time)

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possivel criar o time") from erro

    return novo_time


@router.get("/", response_model=list[RespostaTimes])
def listar_times(torneio_id: int, db: Session = Depends(get_db)):
    try:
        torneio = db.get(Torneio, torneio_id)

        if torneio is None:
            pass

        consulta = select(Time).where(Time.torneio_id == torneio_id)

        times = db.scalars(consulta).all()

        return times

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro


@router.get("/{time_id}", response_model=list[RespostaTimes])
def listar_times_id(torneio_id: int, time_id: int,db: Session = Depends(get_db)):

    try:
        torneio = db.get(Torneio, torneio_id)

        if torneio is None:
            pass

        consulta = select(Time).where(Time.torneio_id == torneio_id)

        time = db.scalar(consulta).all()

        return time

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro



@router.put("/{time_id}", response_model=RespostaTimes)
def atualizar_times(dados: AtualizarTimes, time_id: int,db: Session = Depends(get_db)):
    time = db.get(Time, time_id)

    if time is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar o time")

    dados_atualizados = dados.model_dump()

    for campo, valor in dados_atualizados.itens():
        setattr(time, campo, valor)

    try:
        db.commit()
        db.refresh(time)

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no bando de dados") from erro

    except IntegrityError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Verifique as informação enviadas") from erro


@router.delete("/{time_id}", response_model=RespostaTimes)
def deletar_times(time_id: int, db: Session = Depends(get_db)) -> None:
    time = db.get(Time, time_id)

    if time is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar o time")

    try:
        db.delete(time)
        db.commit()

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro
