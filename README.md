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

## Docker (próxima etapa)

La estructura está preparada para dockerizarse. Se requiere:

1. `Dockerfile` con imagen base Python + OpenCV
2. Montar `config.yaml` como volumen
3. Exponer acceso de red al stream RTSP y broker MQTT
