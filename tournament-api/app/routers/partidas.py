from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.partidas import Partida
from app.models.torneio import Torneio
from app.shemas.partidas import (
    CriarPartidas,
    AtualizarPartidas,
    RespostaPartidas,
)

router = APIRouter(prefix="/torneios/{torneios.id}/partidas", tags=["Partidas"])

@router.post("/", response_model=RespostaPartidas, status_code=status.HTTP_201_CREATED)
def criarpartida(dados: CriarPartidas, db: Session = Depends(get_db)):
    nova_partida = Partida(**dados.model_dump())

    try:
        db.add(nova_partida)
        db.commit()
        db.refresh(nova_partida)

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possivel criar a partida") from erro

    return nova_partida


@router.get("/", response_model=list[RespostaPartidas])
def listar_partidas(torneio_id: int, db: Session = Depends(get_db)):
    
    try:
        torneio = db.get(Torneio, torneio_id)

        if torneio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possicel localizar o torneio")

        consulta = select(Partida).where(Partida.torneio_id == torneio_id)

        partidas = db.scalars(consulta).all()

        return partidas

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro
    

@router.get("/{partida_id}", response_model=list[RespostaPartidas])
def buscar_partida_id(torneio_id: int, partida_id: int, db: Session = Depends(get_db)):

    try:
        torneio = db.get(Torneio, torneio_id)

        if torneio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar o torneio")

        consulta = select(Partida).where(Partida.torneio_id == torneio_id)

        partida = db.scalar(consulta).all()

        return partida

    except SQLAlchemyError as erro:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro


@router.put("/{partidas_id}", response_model=RespostaPartidas)
def atualizar_partida(dados: AtualizarPartidas, partidas_id: int, db: Session = Depends(get_db)):
    partida = db.get(Partida, partidas_id)

    if partida is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar a partida")

    dados_atualizados = dados.model_dump()

    for campo, valor in dados_atualizados.items():
        setattr(partida, campo, valor)

    try:
        db.commit()
        db.refresh(partida)

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erro nos dados enviados") from erro
    


@router.delete("/{partida.id}", resposnse_model=RespostaPartidas)
def deletar_partida(partida_id: int, db: Session = Depends(get_db)) -> None:
    partida = db.get(Partida, partida_id)

    if partida_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar a partida")

    try:
        db.delete(partida)
        db.commit()

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro
