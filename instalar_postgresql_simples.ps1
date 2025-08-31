# Script PowerShell simples para instalar PostgreSQL via winget
# Execute como administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INSTALACAO POSTGRESQL - ACADEMIA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Execute como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "   Clique com botao direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit
}

Write-Host "Executando como administrador" -ForegroundColor Green
Write-Host ""

# 1. Instalar PostgreSQL via winget
Write-Host "Instalando PostgreSQL via winget..." -ForegroundColor Yellow
try {
    winget install PostgreSQL.PostgreSQL --accept-source-agreements --accept-package-agreements
    Write-Host "PostgreSQL instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "Erro ao instalar PostgreSQL" -ForegroundColor Red
    Write-Host "   Instale manualmente: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit
}

Write-Host ""

# 2. Aguardar instalação
Write-Host "Aguardando instalacao terminar..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 3. Configurar arquivo .env
Write-Host "Configurando arquivo .env..." -ForegroundColor Yellow
$envContent = @"
# Configuracoes do PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin123
DB_NAME=academia_amigo_povo

# URL do banco de dados
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/academia_amigo_povo

# Configuracoes da aplicacao
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key
FLASK_ENV=development
DEBUG=True
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "Arquivo .env criado!" -ForegroundColor Green

Write-Host ""

# 4. Instalar dependências Python
Write-Host "Instalando dependencias Python..." -ForegroundColor Yellow
try {
    & "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" -m pip install psycopg2-binary python-dotenv flask flask-sqlalchemy
    Write-Host "Dependencias instaladas!" -ForegroundColor Green
} catch {
    Write-Host "Erro ao instalar dependencias" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Configure a senha do PostgreSQL: admin123" -ForegroundColor White
Write-Host "2. Execute: python configurar_postgresql.py" -ForegroundColor White
Write-Host "3. Execute: python database_setup.py" -ForegroundColor White
Write-Host "4. Execute: python app.py" -ForegroundColor White
Write-Host ""

Write-Host "Link para configuracao manual:" -ForegroundColor Yellow
Write-Host "https://www.postgresql.org/download/windows/" -ForegroundColor White
Write-Host ""

Read-Host "Pressione Enter para sair"
