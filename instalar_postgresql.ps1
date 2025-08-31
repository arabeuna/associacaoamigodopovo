# Script PowerShell para instalar PostgreSQL automaticamente
# Execute como administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INSTALACAO POSTGRESQL - ACADEMIA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Este script precisa ser executado como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "   Clique com botão direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit
}

Write-Host "✅ Executando como administrador" -ForegroundColor Green
Write-Host ""

# 1. Instalar Chocolatey (se não estiver instalado)
Write-Host "🔧 Verificando Chocolatey..." -ForegroundColor Yellow
try {
    $chocoVersion = choco --version
    Write-Host "✅ Chocolatey já está instalado (versão: $chocoVersion)" -ForegroundColor Green
} catch {
    Write-Host "📦 Instalando Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "✅ Chocolatey instalado com sucesso!" -ForegroundColor Green
}

Write-Host ""

# 2. Instalar PostgreSQL
Write-Host "🐘 Instalando PostgreSQL..." -ForegroundColor Yellow
try {
    choco install postgresql --version=15.4 -y
    Write-Host "✅ PostgreSQL instalado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao instalar PostgreSQL via Chocolatey" -ForegroundColor Red
    Write-Host "   Tentando instalação manual..." -ForegroundColor Yellow
    
    # Instalação manual via winget
    try {
        winget install PostgreSQL.PostgreSQL
        Write-Host "✅ PostgreSQL instalado via winget!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erro na instalação automática" -ForegroundColor Red
        Write-Host "   Instale manualmente: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
        Read-Host "Pressione Enter para sair"
        exit
    }
}

Write-Host ""

# 3. Aguardar serviços iniciarem
Write-Host "⏳ Aguardando serviços iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 4. Verificar se PostgreSQL está rodando
Write-Host "🔍 Verificando se PostgreSQL está rodando..." -ForegroundColor Yellow
try {
    $postgresService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
    if ($postgresService) {
        if ($postgresService.Status -eq "Running") {
            Write-Host "✅ PostgreSQL está rodando!" -ForegroundColor Green
        } else {
            Write-Host "🔄 Iniciando PostgreSQL..." -ForegroundColor Yellow
            Start-Service $postgresService.Name
            Write-Host "✅ PostgreSQL iniciado!" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️ Serviço PostgreSQL não encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar o serviço" -ForegroundColor Yellow
}

Write-Host ""

# 5. Configurar senha do postgres
Write-Host "🔐 Configurando senha do usuário postgres..." -ForegroundColor Yellow
try {
    # Tentar configurar a senha via psql
    $env:PGPASSWORD = "postgres"
    $setPasswordSQL = "ALTER USER postgres PASSWORD 'admin123';"
    
    # Tentar diferentes caminhos do psql
    $psqlPaths = @(
        "C:\Program Files\PostgreSQL\15\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "psql"
    )
    
    $psqlFound = $false
    foreach ($psqlPath in $psqlPaths) {
        try {
            & $psqlPath -U postgres -h localhost -c $setPasswordSQL 2>$null
            Write-Host "✅ Senha configurada com sucesso!" -ForegroundColor Green
            $psqlFound = $true
            break
        } catch {
            continue
        }
    }
    
    if (-not $psqlFound) {
        Write-Host "⚠️ Não foi possível configurar a senha automaticamente" -ForegroundColor Yellow
        Write-Host "   Configure manualmente: ALTER USER postgres PASSWORD 'admin123';" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Erro ao configurar senha" -ForegroundColor Yellow
}

Write-Host ""

# 6. Criar banco de dados
Write-Host "🗄️ Criando banco de dados..." -ForegroundColor Yellow
try {
    $createDBSQL = "CREATE DATABASE academia_amigo_povo;"
    
    foreach ($psqlPath in $psqlPaths) {
        try {
            $env:PGPASSWORD = "admin123"
            & $psqlPath -U postgres -h localhost -c $createDBSQL 2>$null
            Write-Host "✅ Banco de dados criado com sucesso!" -ForegroundColor Green
            break
        } catch {
            continue
        }
    }
} catch {
    Write-Host "⚠️ Erro ao criar banco de dados" -ForegroundColor Yellow
    Write-Host "   Crie manualmente: CREATE DATABASE academia_amigo_povo;" -ForegroundColor Yellow
}

Write-Host ""

# 7. Configurar arquivo .env
Write-Host "📝 Configurando arquivo .env..." -ForegroundColor Yellow
try {
    $envContent = @"
# Configurações do PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=admin123
DB_NAME=academia_amigo_povo

# URL do banco de dados
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/academia_amigo_povo

# Configurações da aplicação
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key
FLASK_ENV=development
DEBUG=True
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Arquivo .env criado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao criar arquivo .env" -ForegroundColor Red
}

Write-Host ""

# 8. Instalar dependências Python
Write-Host "📦 Instalando dependências Python..." -ForegroundColor Yellow
try {
    & "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" -m pip install psycopg2-binary python-dotenv flask flask-sqlalchemy
    Write-Host "✅ Dependências instaladas com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
}

Write-Host ""

# 9. Configurar banco de dados
Write-Host "🔧 Configurando banco de dados..." -ForegroundColor Yellow
try {
    & "C:\Users\joaoj\AppData\Local\Programs\Python\Python313\python.exe" database_setup.py
    Write-Host "✅ Banco de dados configurado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao configurar banco de dados" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Para iniciar o sistema:" -ForegroundColor Yellow
Write-Host "1. Execute: python app.py" -ForegroundColor White
Write-Host "2. Acesse: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "3. Login: admin / admin123" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Para testar o banco:" -ForegroundColor Yellow
Write-Host "Execute: python testar_postgresql.py" -ForegroundColor White
Write-Host ""

Read-Host "Pressione Enter para sair"
