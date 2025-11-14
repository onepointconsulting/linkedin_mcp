# Clear Python cache directories
Write-Host "Clearing Python cache directories..." -ForegroundColor Yellow

Get-ChildItem -Path . -Filter __pycache__ -Recurse -Directory | ForEach-Object {
    Write-Host "Removing: $($_.FullName)" -ForegroundColor Gray
    Remove-Item -Path $_.FullName -Recurse -Force
}

Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File | ForEach-Object {
    Write-Host "Removing: $($_.FullName)" -ForegroundColor Gray
    Remove-Item -Path $_.FullName -Force
}

Write-Host "Cache cleared!" -ForegroundColor Green

