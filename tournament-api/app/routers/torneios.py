from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.torneio import Torneio
from app.schemas.torneio import (
    CriarTorneio,
    AtualizarTorneio,
    RespostaTorneio,
)

router = APIRouter(prefix="/torneios", tags=["Torneios"])

@router.post("/", response_model=RespostaTorneio, status_code=status.HTTP_201_REATED)
def criartorneio(dados: CriarTorneio, db: Session = Depends(get_db)):
    novo_torneio = Torneio(**dados.model_dump())

    try:
        db.add(novo_torneio)
        db.commit()
        db.refresh(novo_torneio)
    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possivel cadastrar o torneio") from erro

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados")

    return novo_torneio


@router.get("/", reponse_model=RespostaTorneio)
def listar_torneios(db: Session = Depends(get_db)):
    try:
        consulta = select(Torneio).order_by(Torneio.id)

        torneios = consulta.scalar(consulta).all()

        return torneios
    
    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

@router.get("/{torneio.id}", resposnse_model=RespostaTorneio)
def buscar_torneio_id(db: Session = Depends(get_db)):
    try:

        consulta = db.get(Torneio, torneio.id)

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Torneio não encontrado")

    return Torneio

@router.put("/{torneio.id}", response_model=RespostaTorneio)
def atualizar_torneio(db: Session = Depends(get_db)):
    pass


@router.delete("/{torneio.id}", response_model=RespostaTorneio)
def deletar_torneio(db: Session = Depends(get_db)):
    pass

    
