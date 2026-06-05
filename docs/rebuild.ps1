# rebuild.ps1 — Clean and rebuild Sphinx HTML docs
Push-Location $PSScriptRoot

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "source/automod") { Remove-Item -Recurse -Force "source/automod" }

python -m sphinx -M html source build

Pop-Location
