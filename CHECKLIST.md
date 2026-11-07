# Production checklist: loan-api:prod

- GitHub: https://github.com/<your-name>/loan-api
- Docker Hub: https://hub.docker.com/r/<your-name>/loan-api

> Under each command, paste the real output or link a screenshot.

---

## 1. Multi-stage Dockerfile.prod: slim base, non-root user, HEALTHCHECK

**File review:** `Dockerfile.prod` has two stages (`FROM python:3.13-slim AS builder` and then `FROM python:3.13-slim`), sets `USER appuser` and has a `HEALTHCHECK` on `/health`.

```bash
grep -nE "^FROM|^USER|^HEALTHCHECK" Dockerfile.prod
docker run --rm loan-api:prod whoami
docker compose ps
```
```text
<paste: whoami → appuser; api row shows "Up ... (healthy)">
```

## 2. .dockerignore excludes Git, caches, local models and dev config

**File review:** `.dockerignore` excludes `.git`, `__pycache__/`, `.pytest_cache/`, `models/`, `mlruns/`, `.devcontainer/`, `.vscode/`, `.env`, `requirements-dev.txt` and `tests/`.

```bash
cat .dockerignore
docker run --rm loan-api:prod ls -la /app
```
```text
<paste: /app contains only main.py and model/>
```

## 3. Model path configurable with MODEL_PATH

```bash
docker run -d --rm --name loan-110 -p 8001:8000 \
  -v "$PWD/models:/models:ro" \
  -e MODEL_PATH=/models/loan_model_1.1.0.joblib \
  loan-api:prod
sleep 5 && curl -s localhost:8001/health
docker stop loan-110
```
```text
<paste: {"status":"ok","model_version":"1.1.0"}>
```

## 4. compose.yaml runs API + PostgreSQL + Adminer, with the API built from Dockerfile.prod

```bash
grep -nA2 "build:" compose.yaml
docker compose up -d --build
docker compose ps
```
```text
<paste: api Up (healthy), db Up (healthy), adminer Up>
```

## 5. Image at least 40% smaller than the full-Python variant

```bash
docker build -t loan-api:full -f Dockerfile .
docker images loan-api
```
```text
<paste: loan-api:full ≈ 1.6 GB, loan-api:prod ≈ 5xx MB>
```
Reduction = (full − prod) / full = <xx>% (must be ≥ 40%)

## 6. No HIGH or CRITICAL findings without a note

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest \
  image --severity HIGH,CRITICAL loan-api:prod
```
```text
<paste Trivy report>
```

| CVE | Package | Severity | Note |
|-----|---------|----------|------|
| _none_ | | | `apt-get upgrade` was added and the image rebuilt; 0 HIGH/CRITICAL |
<!-- one row per remaining finding, for example:
| CVE-2025-XXXX | libc6 | HIGH | Debian has no fixed version yet; the API does not use the affected function; will rebuild when a fix is released |
| CVE-2025-YYYY | starlette | HIGH | Fixed: bumped to x.y.z in requirements.txt and rebuilt |
-->

## 7. Image published as <your-name>/loan-api:1.0.0 and :latest

```bash
docker login -u $DOCKER_USER   # paste access token
DOCKER_USER=your-dockerhub-username   # change this to your username

docker build -t loan-api:prod -f Dockerfile.prod .
docker tag loan-api:prod $DOCKER_USER/loan-api:1.0.0
docker tag loan-api:prod $DOCKER_USER/loan-api:latest
docker push $DOCKER_USER/loan-api:1.0.0
docker push $DOCKER_USER/loan-api:latest
```
Screenshot: `screenshots/dockerhub-tags.png`, showing https://hub.docker.com/r/<your-name>/loan-api/tags with both tags at the same size

---

## Pull and run from the registry (no local files)

```bash
docker compose down
docker rmi $DOCKER_USER/loan-api:1.0.0 $DOCKER_USER/loan-api:latest loan-api:prod
docker run --rm -p 8000:8000 $DOCKER_USER/loan-api:1.0.0
```
Expected output: `Unable to find image ... locally`, then the layers download, then `Uvicorn running on http://0.0.0.0:8000`.
Screenshot: `screenshots/docs-200.png`, showing /docs with POST /predict and a 200 response

## Secrets

- The repo has no `.env` or tokens. The Docker Hub token is used only at `docker login` and is never written to a file.
- The only password is the development-only `POSTGRES_PASSWORD` in compose.yaml, which the brief allows.
