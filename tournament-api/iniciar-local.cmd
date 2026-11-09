@echo off
cd /d "%~dp0"
set "DATABASE_URL=sqlite:///./racha-local.db"
if not exist ".venv\Scripts\python.exe" (
  echo Instalando as dependencias pela primeira vez...
  uv sync
  if errorlevel 1 (
    echo Nao foi possivel preparar o ambiente. Instale o uv e tente novamente.
    pause
    exit /b 1
  )
)
echo.
echo RACHA! disponivel em http://127.0.0.1:8000/
echo Deixe esta janela aberta enquanto estiver usando o site.
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
