# 🚀 Script de Deploy Automático
# Execute este script para preparar os arquivos para produção

param(
    [Parameter(Mandatory=$true)]
    [string]$RailwayURL,
    
    [Parameter(Mandatory=$false)]
    [string]$NetlifyURL = ""
)

Write-Host "🔧 Preparando deploy para produção..." -ForegroundColor Cyan

# Verificar se a URL do Railway foi fornecida
if (-not $RailwayURL) {
    Write-Host "❌ Erro: URL do Railway é obrigatória!" -ForegroundColor Red
    Write-Host "Uso: .\deploy-setup.ps1 -RailwayURL 'https://web-production-xxxx.up.railway.app'" -ForegroundColor Yellow
    exit 1
}

# Limpar URL (remover barra final se existir)
$RailwayURL = $RailwayURL.TrimEnd('/')

Write-Host "📡 URL do Backend (Railway): $RailwayURL" -ForegroundColor Green

# 1. Atualizar config-auto.js com a URL do Railway
Write-Host "🔄 Atualizando configuração automática..." -ForegroundColor Yellow

$configAutoPath = "frontend\js\config-auto.js"
$configContent = Get-Content $configAutoPath -Raw

# Substituir a URL placeholder
$newConfigContent = $configContent -replace "https://SEU-BACKEND-RAILWAY\.up\.railway\.app", $RailwayURL

Set-Content -Path $configAutoPath -Value $newConfigContent -Encoding UTF8

Write-Host "✅ config-auto.js atualizado!" -ForegroundColor Green

# 2. Atualizar netlify.toml
Write-Host "🔄 Atualizando netlify.toml..." -ForegroundColor Yellow

$netlifyTomlPath = "netlify.toml"
$netlifyContent = Get-Content $netlifyTomlPath -Raw

# Substituir a URL no netlify.toml
$newNetlifyContent = $netlifyContent -replace "https://sua-api-railway\.up\.railway\.app", $RailwayURL

Set-Content -Path $netlifyTomlPath -Value $newNetlifyContent -Encoding UTF8

Write-Host "✅ netlify.toml atualizado!" -ForegroundColor Green

# 3. Verificar estrutura de arquivos
Write-Host "🔍 Verificando arquivos de deploy..." -ForegroundColor Yellow

$filesToCheck = @(
    "railway.json",
    "backend\Procfile", 
    "backend\requirements.txt",
    "backend\src\app_postgresql.py",
    "netlify.toml",
    "frontend\js\config-auto.js"
)

$allFilesExist = $true
foreach ($file in $filesToCheck) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "❌ Alguns arquivos estão faltando!" -ForegroundColor Red
    exit 1
}

# 4. Mostrar próximos passos
Write-Host "`n🎉 Deploy preparado com sucesso!" -ForegroundColor Green
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Faça commit das alterações no GitHub" -ForegroundColor White
Write-Host "   2. Deploy no Railway (backend):" -ForegroundColor White
Write-Host "      - Novo projeto > Deploy from GitHub" -ForegroundColor Gray
Write-Host "      - Adicionar PostgreSQL" -ForegroundColor Gray
Write-Host "      - Configurar variáveis de ambiente" -ForegroundColor Gray
Write-Host "   3. Deploy no Netlify (frontend):" -ForegroundColor White
Write-Host "      - Novo site > GitHub > pasta 'frontend'" -ForegroundColor Gray
Write-Host "   4. Testar sistema online!" -ForegroundColor White

if ($NetlifyURL) {
    Write-Host "`n🌐 URLs configuradas:" -ForegroundColor Cyan
    Write-Host "   Backend:  $RailwayURL" -ForegroundColor White
    Write-Host "   Frontend: $NetlifyURL" -ForegroundColor White
}

Write-Host "`n💡 Dica: Execute 'git status' para ver as alterações" -ForegroundColor Yellow