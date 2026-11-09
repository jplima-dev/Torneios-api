from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database.database import Base, engine
from app.models import fase, partidas as modelo_partidas, times as modelo_times, torneio as modelo_torneio  # noqa: F401
from app.routers import fases, partidas, times, torneios

WEB = Path(__file__).parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="API de torneios",
    description="API para criar e gerenciar torneios",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(torneios.router)
app.include_router(partidas.router)
app.include_router(times.router)
app.include_router(fases.router)
app.mount("/assets", StaticFiles(directory=WEB), name="assets")

@app.get("/")
def home():
    return FileResponse(WEB / "index.html")


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(WEB / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    return FileResponse(WEB / "sw.js", media_type="application/javascript", headers={"Cache-Control": "no-cache"})
