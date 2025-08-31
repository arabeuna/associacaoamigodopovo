# Script rapido para instalar PostgreSQL
Write-Host "Instalando PostgreSQL via winget..." -ForegroundColor Yellow

# Tentar instalar via winget
try {
    winget install PostgreSQL.PostgreSQL --accept-source-agreements --accept-package-agreements
    Write-Host "PostgreSQL instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "Erro na instalacao automatica" -ForegroundColor Red
    Write-Host "Instale manualmente: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Aguardando instalacao..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Criar arquivo .env
Write-Host "Criando arquivo .env..." -ForegroundColor Yellow
$envContent = @"
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin123
DB_NAME=academia_amigo_povo
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/academia_amigo_povo
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key
FLASK_ENV=development
DEBUG=True
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "Arquivo .env criado!" -ForegroundColor Green

# Instalar dependencias Python
Write-Host "Instalando dependencias Python..." -ForegroundColor Yellow
try {
    & "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" -m pip install psycopg2-binary python-dotenv flask flask-sqlalchemy
    Write-Host "Dependencias instaladas!" -ForegroundColor Green
} catch {
    Write-Host "Erro ao instalar dependencias" -ForegroundColor Red
}

Write-Host ""
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Configure a senha do PostgreSQL: admin123" -ForegroundColor White
Write-Host "2. Execute: python configurar_postgresql.py" -ForegroundColor White
Write-Host "3. Execute: python database_setup.py" -ForegroundColor White
Write-Host "4. Execute: python app.py" -ForegroundColor White
