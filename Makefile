IMAGE = fvillarino/video-ai-detector
VERSION = 1.0.0

build:
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

push:
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

run:
	.venv\Scripts\python.exe main.py

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f camera-ai
