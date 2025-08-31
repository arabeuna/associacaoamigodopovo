@echo off
echo ========================================
echo    INSTALACAO POSTGRESQL - ACADEMIA
echo ========================================
echo.

echo 📥 Baixando PostgreSQL...
echo.
echo 🔗 Link para download: https://www.postgresql.org/download/windows/
echo.
echo 📋 INSTRUCOES DE INSTALACAO:
echo 1. Baixe o PostgreSQL 15 ou 16
echo 2. Execute o instalador
echo 3. Use a senha: admin123
echo 4. Mantenha a porta: 5432
echo 5. Instale todos os componentes
echo.
echo ⏳ Aguarde a instalacao terminar...
echo.
pause

echo.
echo 🔧 Configurando sistema...
echo.

REM Executar script de configuração
"C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" configurar_postgresql.py

echo.
echo ✅ Configuracao concluida!
echo.
echo 🚀 Para iniciar o sistema:
echo 1. Execute: python database_setup.py
echo 2. Execute: python app.py
echo 3. Acesse: http://127.0.0.1:5000
echo.
pause
