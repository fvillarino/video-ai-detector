IMAGE = ghcr.io/fvillarino/video-ai-detector
VERSION = 1.0.0

# El build y push oficial los hace GitHub Actions al pushear un tag v*
# (ver .github/workflows/docker-publish.yml). Los targets build/push quedan
# como fallback para publicar manualmente desde local.
build:
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

push:
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

run:
	.venv\Scripts\python.exe main.py

# --- Beelink ---
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f camera-ai

# Actualizar el servicio a la versión fijada en .env (APP_VERSION).
deploy:
	docker compose pull
	docker compose up -d
