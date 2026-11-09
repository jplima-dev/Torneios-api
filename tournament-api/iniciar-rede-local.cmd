@echo off
cd /d "%~dp0"
set "DATABASE_URL=sqlite:///./racha-local.db"
if not exist ".venv\Scripts\python.exe" (
  echo Instalando as dependencias pela primeira vez...
  uv sync
  if errorlevel 1 (
    echo Nao foi possivel preparar o ambiente.
    pause
    exit /b 1
  )
)
echo.
echo Enderecos IPv4 deste PC:
ipconfig | findstr /i "IPv4"
echo.
echo No app Android, use http://IP_DO_PC:8000
echo Deixe esta janela aberta durante o jogo.
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
