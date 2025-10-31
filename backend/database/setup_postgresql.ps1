# Script PowerShell para configurar PostgreSQL no Windows

Write-Host "=== Configuração do PostgreSQL para Gestão de Indicadores ===" -ForegroundColor Green

# Verificar se PostgreSQL está instalado
$pgPath = Get-Command "psql" -ErrorAction SilentlyContinue

if (-not $pgPath) {
    Write-Host "PostgreSQL não encontrado. Vamos instalar..." -ForegroundColor Yellow
    
    # Verificar se Chocolatey está instalado
    $chocoPath = Get-Command "choco" -ErrorAction SilentlyContinue
    
    if (-not $chocoPath) {
        Write-Host "Instalando Chocolatey..." -ForegroundColor Blue
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    
    Write-Host "Instalando PostgreSQL via Chocolatey..." -ForegroundColor Blue
    choco install postgresql -y
    
    # Atualizar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "PostgreSQL instalado! Reinicie o terminal e execute novamente." -ForegroundColor Green
    exit
}

Write-Host "PostgreSQL encontrado: $($pgPath.Source)" -ForegroundColor Green

# Configurar variáveis
$DB_NAME = "gestao_indicadores"
$DB_USER = "postgres"
$DB_PASSWORD = Read-Host "Digite a senha do PostgreSQL (deixe vazio para 'postgres')"
if (-not $DB_PASSWORD) { $DB_PASSWORD = "postgres" }

# Testar conexão
Write-Host "Testando conexão com PostgreSQL..." -ForegroundColor Blue
$env:PGPASSWORD = $DB_PASSWORD

try {
    psql -U $DB_USER -d postgres -c "SELECT version();" | Out-Null
    Write-Host "Conexão bem-sucedida!" -ForegroundColor Green
}
catch {
    Write-Host "Erro ao conectar. Verifique se o PostgreSQL está rodando e a senha está correta." -ForegroundColor Red
    exit 1
}

# Verificar se banco existe
$dbExists = psql -U $DB_USER -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';"

if ($dbExists -match "1") {
    Write-Host "Banco de dados '$DB_NAME' já existe." -ForegroundColor Yellow
    $recreate = Read-Host "Deseja recriar o banco? (s/N)"
    
    if ($recreate -eq "s" -or $recreate -eq "S") {
        Write-Host "Removendo banco existente..." -ForegroundColor Yellow
        dropdb -U $DB_USER $DB_NAME
        
        Write-Host "Criando novo banco..." -ForegroundColor Blue
        createdb -U $DB_USER $DB_NAME
    }
}
else {
    Write-Host "Criando banco de dados '$DB_NAME'..." -ForegroundColor Blue
    createdb -U $DB_USER $DB_NAME
}

# Executar schema
Write-Host "Executando schema do banco..." -ForegroundColor Blue
$schemaPath = Join-Path $PSScriptRoot "schema.sql"

if (Test-Path $schemaPath) {
    psql -U $DB_USER -d $DB_NAME -f $schemaPath
    Write-Host "Schema executado com sucesso!" -ForegroundColor Green
}
else {
    Write-Host "Arquivo schema.sql não encontrado em: $schemaPath" -ForegroundColor Red
}

# Criar arquivo .env
Write-Host "Criando arquivo .env..." -ForegroundColor Blue
$envPath = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"

$envContent = @"
# Configurações gerais
SECRET_KEY=gestao-indicadores-secret-key-$(Get-Random)
JWT_SECRET_KEY=jwt-secret-key-$(Get-Random)

# Configurações do banco PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Ambiente
FLASK_ENV=development
FLASK_DEBUG=True
"@

$envContent | Out-File -FilePath $envPath -Encoding UTF8
Write-Host "Arquivo .env criado em: $envPath" -ForegroundColor Green

# Instalar dependências Python
Write-Host "Instalando dependências Python..." -ForegroundColor Blue
$backendPath = Split-Path $PSScriptRoot -Parent
Push-Location $backendPath

try {
    pip install -r requirements.txt
    Write-Host "Dependências instaladas com sucesso!" -ForegroundColor Green
}
catch {
    Write-Host "Erro ao instalar dependências. Execute manualmente: pip install -r requirements.txt" -ForegroundColor Yellow
}

Pop-Location

Write-Host ""
Write-Host "=== Configuração Concluída ===" -ForegroundColor Green
Write-Host "Para iniciar a aplicação:" -ForegroundColor White
Write-Host "  cd backend/src" -ForegroundColor Cyan
Write-Host "  python app_postgresql.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usuários padrão criados:" -ForegroundColor White
Write-Host "  admin@hospital.com (senha: admin123) - Role: admin" -ForegroundColor Cyan
Write-Host "  gestor@hospital.com (senha: gestor123) - Role: gestor" -ForegroundColor Cyan
Write-Host "  operador@hospital.com (senha: operador123) - Role: operador" -ForegroundColor Cyan
Write-Host ""
Write-Host "API estará disponível em: http://localhost:5000" -ForegroundColor Yellow