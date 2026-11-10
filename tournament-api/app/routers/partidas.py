from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.partidas import Partida
from app.models.torneio import Torneio
from app.models.fase import Fase
from app.models.times import Times
from app.shemas.partidas import (
    AtualizarPartidas,
    CriarPartidas,
    RespostaPartidas,
)

router = APIRouter(prefix="/torneios/{torneio_id}/partidas", tags=["Partidas"])

@router.post("/", response_model=RespostaPartidas, status_code=status.HTTP_201_CREATED)
def criarpartida(torneio_id: int, dados: CriarPartidas, db: Session = Depends(get_db)):
    torneio = db.get(Torneio, torneio_id)

    if torneio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possível localizar o torneio")

    fase = db.get(Fase, dados.fase_id)

    if fase is None or fase.torneio_id != torneio_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A fase não pertence a este torneio")

    if dados.time1_id == dados.time2_id:
        raise HTTPException(status_code=400, detail="Escolha dois times diferentes")
    for time_id in (dados.time1_id, dados.time2_id):
        time = db.get(Times, time_id)
        if time is None or time.torneio_id != torneio_id:
            raise HTTPException(status_code=400, detail="Os times devem pertencer ao torneio")

    dados_partida = dados.model_dump()
    dados_partida["torneio_id"] = torneio_id
    nova_partida = Partida(**dados_partida)

    try:
        db.add(nova_partida)
        db.commit()
        db.refresh(nova_partida)

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possivel criar a partida") from erro

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    return nova_partida


@router.post("/{partida_id}/ponto", response_model=RespostaPartidas)
def alterar_ponto(torneio_id: int, partida_id: int, lado: int, delta: int = 1, db: Session = Depends(get_db)):
    if lado not in (1, 2) or delta not in (-3, -2, -1, 1, 2, 3):
        raise HTTPException(400, "Informe lado 1 ou 2 e delta entre -3 e 3, exceto zero")
    coluna = Partida.pontos1 if lado == 1 else Partida.pontos2
    resultado = db.execute(
        update(Partida)
        .where(Partida.id == partida_id, Partida.torneio_id == torneio_id, coluna + delta >= 0)
        .values({coluna: coluna + delta})
    )
    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(404, "Partida não encontrada ou placar já está em zero")
    db.commit()
    return db.get(Partida, partida_id)


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


@router.get("/{partida_id}", response_model=RespostaPartidas)
def buscar_partida_id(torneio_id: int, partida_id: int, db: Session = Depends(get_db)):

    try:
        torneio = db.get(Torneio, torneio_id)

        if torneio is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar o torneio")

        consulta = select(Partida).where(Partida.torneio_id == torneio_id, Partida.id == partida_id)

        partida = db.scalar(consulta)

        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possível localizar a partida")

        return partida

    except SQLAlchemyError as erro:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro


@router.put("/{partidas_id}", response_model=RespostaPartidas)
def atualizar_partida(dados: AtualizarPartidas, partidas_id: int, torneio_id: int, db: Session = Depends(get_db)):
    partida = db.get(Partida, partidas_id)

    if partida is None or partida.torneio_id != torneio_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar a partida")

    dados_atualizados = dados.model_dump(exclude_unset=True)

    if "fase_id" in dados_atualizados:
        fase = db.get(Fase, dados_atualizados["fase_id"])

        if fase is None or fase.torneio_id != torneio_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A fase não pertence a este torneio")

    for campo, valor in dados_atualizados.items():
        setattr(partida, campo, valor)

    try:
        db.commit()
        db.refresh(partida)

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erro nos dados enviados") from erro

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    return partida


@router.delete("/{partida_id}", response_model=RespostaPartidas)
def deletar_partida(torneio_id: int, partida_id: int, db: Session = Depends(get_db)):
    partida = db.get(Partida, partida_id)

    if partida is None or partida.torneio_id != torneio_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não foi possivel localizar a partida")

    try:
        db.delete(partida)
        db.commit()

    except IntegrityError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erro ao excluir a partida") from erro

    except SQLAlchemyError as erro:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no banco de dados") from erro

    return partida
