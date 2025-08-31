Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Academia Amigo do Povo - Sistema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando o sistema..." -ForegroundColor Green
Write-Host ""

# Usar o Python instalado localmente
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" app.py

Write-Host ""
Write-Host "Sistema encerrado." -ForegroundColor Yellow
Read-Host "Pressione Enter para sair"
