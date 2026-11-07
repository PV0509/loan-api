# Usage (PowerShell):  .\run_all.ps1 -DockerUser phavy
param([Parameter(Mandatory=$true)][string]$DockerUser)

Write-Host "== 1 & 4: stack on production image =="
docker compose up -d --build
Start-Sleep 30; docker compose ps
docker run --rm loan-api:prod whoami

Write-Host "== 2: image contents =="
docker run --rm loan-api:prod ls -la /app

Write-Host "== 3: MODEL_PATH with mounted 1.1.0 model =="
docker run -d --rm --name loan-110 -p 8001:8000 -v "${PWD}/models:/models:ro" -e MODEL_PATH=/models/loan_model_1.1.0.joblib loan-api:prod
Start-Sleep 8; curl.exe -s localhost:8001/health; Write-Host ""; docker stop loan-110

Write-Host "== 5: size vs full-Python =="
docker build -t loan-api:full -f Dockerfile .
docker images loan-api

Write-Host "== 6: Trivy =="
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity HIGH,CRITICAL loan-api:prod
