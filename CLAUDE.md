# CLAUDE.md

Guía para Claude Code al trabajar en este repositorio. Léela antes de planificar o escribir código.

## Qué es este proyecto

POC de detección de personas (y otras clases YOLO) en streams RTSP de cámaras Dahua,
con publicación de eventos en MQTT para integrarse con Home Assistant. La prioridad es
ser **simple, claro y estable**, no enterprise. Evitá la sobreingeniería.

El estado y los requisitos de la POC inicial están documentados en
[specs/000-baseline/spec.md](specs/000-baseline/spec.md).

## Arquitectura

```
main.py                  Punto de entrada: carga config, lanza un thread por cámara
config.yaml              Configuración real (NO se commitea; ver config.yaml.example)
detector/yolo_detector.py  YoloDetector: inferencia YOLOv8, devuelve list[Detection]
stream/rtsp_reader.py      RTSPReader: generador de frames con reconexión automática
messaging/mqtt_client.py   MQTTClient: publicación MQTT thread-safe, reconexión
utils/logger.py            get_logger(name, level) configurado
utils/rate_limit.py        CooldownRateLimiter: una acción por key cada N segundos
utils/snapshot.py          save_snapshot(): guarda JPEG y devuelve URL pública
models/                    Modelos YOLO (.pt descargados automáticamente, no commiteados)
```

**Modelo mental del flujo:**
1. `main.py` lee `config.yaml`, crea el `MQTTClient` y el `YoloDetector` **compartidos**.
2. Por cada entrada en `cameras:` lanza un thread daemon que corre `camera_loop`.
3. Cada `camera_loop` itera frames del `RTSPReader`, procesa 1 de cada N, detecta,
   aplica cooldown por `camera:clase`, guarda snapshot y publica en MQTT.
4. SIGINT/SIGTERM setean un `stop_event` compartido para un cierre limpio.

**Decisiones clave (respetar salvo que el spec lo cambie):**
- El detector YOLO y el cliente MQTT son **únicos y compartidos** entre threads.
- Un thread por cámara, todos daemon, coordinados por un único `threading.Event`.
- El rate limiting es un cooldown fijo por `camera_name:class_name`.
- La config es la única fuente de parámetros; nada sensible hardcodeado en código.

## Stack y entorno

- Python 3.10+ (la imagen Docker usa 3.11-slim).
- Dependencias: `ultralytics` (YOLOv8), `opencv-python-headless`, `paho-mqtt`, `PyYAML`.
- Desarrollo en **Windows + PowerShell**. Deploy vía Docker (`docker-compose.yml`) en Linux.
- Entorno virtual en `.venv\`.

## Comandos

```powershell
# Setup local
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Correr local (requiere config.yaml a partir de config.yaml.example)
python main.py            # o:  make run

# Docker (local)
make build                # build manual de la imagen (fallback; el publish oficial es CI)
make up                   # docker compose up -d
make logs                 # seguir logs del contenedor
make down

# Deploy en el Beelink (versión fijada en .env -> APP_VERSION)
make deploy               # docker compose pull && up -d
```

## Release y CI/CD

La imagen se publica en **GHCR** (`ghcr.io/fvillarino/video-ai-detector`) vía GitHub Actions
([.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml)) al pushear un tag
`v*`. Tags de imagen: el git tag (`v1.0.1`), `sha-<commit>` y `latest`. Build `linux/amd64`
(el Beelink es x86_64). El deploy es **manual**: en el server se fija `APP_VERSION` en `.env` y
se corre `make deploy`. Detalle completo en [specs/001-ci-cd-docker/](specs/001-ci-cd-docker/).

No hay suite de tests todavía. Si agregás features con lógica no trivial
(rate limiting, parsing de config, construcción de payload), agregá tests con `pytest`
en `tests/` y documentá cómo correrlos.

## Convenciones de código

- **Nombres en inglés** (funciones, variables, clases); **comentarios y logs en español**.
- Funciones chicas, tipado donde aporte, manejo de errores básico pero presente.
- Logs claros con el identificador de cámara: conexión RTSP, reconexión, detección, publicación.
- Errores que hay que contemplar siempre: stream no disponible, MQTT no disponible, modelo no encontrado.
- Evitar metaprogramación y dependencias innecesarias.
- No commitear secretos: `config.yaml`, `*.pt`, `snapshots/` y `.venv/` están en `.gitignore`.

## Flujo de trabajo: Spec-Driven Development (SDD)

Toda mejora o feature nuevo de tamaño no trivial sigue este flujo **antes** de escribir código.
Los artefactos viven en [`specs/`](specs/). Lee [specs/README.md](specs/README.md) para el detalle.

1. **Spec** (`specs/NNN-nombre/spec.md`) — el *qué* y el *por qué*. Problema, objetivo,
   requisitos, criterios de aceptación. Sin detalles de implementación.
2. **Plan** (`specs/NNN-nombre/plan.md`) — el *cómo*. Enfoque técnico, archivos a tocar,
   cambios de config, riesgos. Requiere que el spec esté acordado.
3. **Tasks** (`specs/NNN-nombre/tasks.md`) — pasos accionables y verificables, en orden.
4. **Implementar** — recién acá se escribe código, siguiendo las tasks y marcándolas.

Reglas para Claude:
- Para un cambio nuevo, **proponé/actualizá el spec primero** y confirmá con el usuario
  antes de saltar a implementar. Para fixes triviales o de una línea, no hace falta spec.
- Mantené los tres artefactos sincronizados con lo que realmente se implementó.
- Usá las plantillas de [`specs/_templates/`](specs/_templates/).
- El estado actual de la POC está documentado como baseline en
  [specs/000-baseline/spec.md](specs/000-baseline/spec.md).

## Roadmap (ideas para próximos specs)

Soporte de más clases (`car`, `dog`), zonas de interés (ROI), integración más rica con
Home Assistant, métricas/health-check, tests automatizados. No implementar hasta que
tengan su propio spec.
