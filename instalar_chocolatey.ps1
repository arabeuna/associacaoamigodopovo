# Instalar Chocolatey e PostgreSQL
Write-Host "Instalando Chocolatey..." -ForegroundColor Yellow

# Instalar Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

Write-Host "Chocolatey instalado!" -ForegroundColor Green
Write-Host ""

Write-Host "Instalando PostgreSQL via Chocolatey..." -ForegroundColor Yellow
choco install postgresql --version=15.4 -y

Write-Host "PostgreSQL instalado!" -ForegroundColor Green
Write-Host ""

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

Write-Host ""
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "Execute: python configurar_postgresql.py" -ForegroundColor Yellow
