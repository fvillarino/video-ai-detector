# video-ai-detector

POC de detección de personas en streams RTSP usando YOLOv8n con publicación en MQTT.

## Estructura

```
├── main.py                  # Punto de entrada
├── config.yaml              # Configuración
├── requirements.txt
├── detector/
│   └── yolo_detector.py     # Inferencia YOLOv8
├── stream/
│   └── rtsp_reader.py       # Lectura RTSP con reconexión
├── messaging/
│   └── mqtt_client.py       # Publicación MQTT
├── utils/
│   ├── logger.py            # Logger configurado
│   └── rate_limit.py        # Cooldown por clase/cámara
└── models/                  # Modelos YOLO (descargados automáticamente)
```

## Requisitos

- Python 3.10+
- Acceso a la cámara RTSP Dahua
- Broker MQTT accesible (ej: Mosquitto)

## Instalación

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Editar `config.yaml` y ajustar:

| Campo | Descripción |
|---|---|
| `camera.rtsp_url` | URL RTSP completa de la cámara |
| `camera.name` | Nombre identificador de la cámara |
| `detection.confidence_threshold` | Confianza mínima (0.0–1.0) |
| `detection.cooldown_seconds` | Tiempo mínimo entre eventos MQTT |
| `mqtt.host` | IP o hostname del broker MQTT |
| `mqtt.username` / `mqtt.password` | Credenciales MQTT |
| `mqtt.topic` | Topic donde se publican los eventos |

## Correr

```bash
python main.py
```

La primera ejecución descargará automáticamente el modelo `yolov8n.pt`.

## Payload MQTT publicado

Cuando se detecta una persona:

```json
{
  "event": "person_detected",
  "camera": "cochera",
  "confidence": 0.83,
  "timestamp": "2026-03-16T00:00:00Z"
}
```

## Release y deploy

La imagen Docker se publica automáticamente en **GHCR**
(`ghcr.io/fvillarino/video-ai-detector`) mediante GitHub Actions al pushear un tag de versión.

### Cortar un release

```bash
git tag v1.0.1
git push origin v1.0.1
```

El workflow buildea la imagen `linux/amd64` y la publica con los tags `v1.0.1`, `sha-<commit>` y `latest`.

> La primera vez, marcá el package como **público** en GitHub (repo → Packages → package settings)
> para que el servidor pueda pullear sin login.

### Deploy en el servidor (Beelink)

El servidor corre un `docker-compose.yml` **suelto** (no es un clon del repo): el servicio
`camera-ai` más un nginx que sirve los snapshots, con `config.yaml`, `snapshots/` y `models/`
montados como volúmenes y `network_mode: host`.

Para desplegar una versión nueva, apuntá la imagen al tag publicado en GHCR y actualizá:

```bash
# en el server, en la carpeta del docker-compose.yml
# editar la línea image: a ghcr.io/fvillarino/video-ai-detector:<tag>   (ej. v1.0.1)
docker compose pull
docker compose up -d
docker compose logs -f camera-ai     # verificar
```

> **Si en cambio corrés desde un checkout del repo:** el `docker-compose.yml` versionado usa
> `${APP_VERSION:-latest}`. En ese caso, fijá la versión con `cp .env.example .env` (editar
> `APP_VERSION`) y usá `make deploy` (= `docker compose pull && up -d`).
