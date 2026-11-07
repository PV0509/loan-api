#!/usr/bin/env bash
# Usage: ./run_all.sh <dockerhub-username>
set -euo pipefail
export DOCKER_USER=${1:?give your Docker Hub username}

echo "== 1 & 4: stack on production image =="
docker compose up -d --build
sleep 30; docker compose ps
docker run --rm loan-api:prod whoami

echo "== 2: image contents =="
docker run --rm loan-api:prod ls -la /app

echo "== 3: MODEL_PATH with mounted 1.1.0 model =="
docker run -d --rm --name loan-110 -p 8001:8000 -v "$PWD/models:/models:ro" \
  -e MODEL_PATH=/models/loan_model_1.1.0.joblib loan-api:prod
sleep 8; curl -s localhost:8001/health; echo; docker stop loan-110

echo "== 5: size vs full-Python =="
docker build -t loan-api:full -f Dockerfile .
docker images loan-api

echo "== 6: Trivy =="
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --severity HIGH,CRITICAL loan-api:prod

echo "== 7: publish =="
docker login -u $DOCKER_USER
docker build -t loan-api:prod -f Dockerfile.prod .
docker tag loan-api:prod $DOCKER_USER/loan-api:1.0.0
docker tag loan-api:prod $DOCKER_USER/loan-api:latest
docker push $DOCKER_USER/loan-api:1.0.0
docker push $DOCKER_USER/loan-api:latest

echo "== Step 4: pull & run from registry =="
docker compose down
docker rmi $DOCKER_USER/loan-api:1.0.0 $DOCKER_USER/loan-api:latest loan-api:prod
docker run --rm -p 8000:8000 $DOCKER_USER/loan-api:1.0.0
