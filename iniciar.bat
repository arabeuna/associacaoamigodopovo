@echo off
echo ========================================
echo   ACADEMIA AMIGO DO POVO - SISTEMA SIMPLES
echo ========================================
echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando o sistema...
echo Acesse: http://localhost:5000
echo.
echo Para parar o sistema, pressione Ctrl+C
echo.

python app.py
pause
