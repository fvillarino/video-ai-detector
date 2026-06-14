# Spec 000 — Baseline (POC actual)

- **Estado:** Implementado
- **Autor:** Federico Villarino
- **Fecha:** 2026-06-14

> Este spec documenta **retroactivamente** la POC ya construida (originalmente con Copilot).
> Sirve como punto de partida y referencia de arquitectura para los próximos specs.
> No describe un cambio pendiente.

## Problema

Se necesita validar rápidamente la detección de personas en cámaras Dahua RTSP y publicar
eventos en MQTT para integrarlos con Home Assistant, sin construir todavía una solución
enterprise.

## Objetivo

Una app Python simple, modular y estable que detecte personas en uno o más streams RTSP
con YOLOv8n y publique un evento MQTT (con snapshot) por detección, respetando un cooldown.

## Alcance

### Incluye
- Múltiples cámaras configurables (lista `cameras:`), un thread daemon por cámara.
- Detector YOLOv8n **compartido** entre threads.
- Cliente MQTT **compartido** entre threads, thread-safe.
- Rate limiting por `camera_name:class_name` mediante cooldown fijo.
- Reconexión automática del stream RTSP y del broker MQTT.
- Guardado de snapshot JPEG por detección, organizado por `snapshots/{camera}/`.
- URL pública del snapshot incluida en el payload MQTT.
- Configuración centralizada en `config.yaml`; payload configurable vía `publish:`.
- Logs claros con identificador de cámara y cierre limpio ante SIGINT/SIGTERM.
- Dockerización: `Dockerfile`, `docker-compose.yml` (incl. nginx para servir snapshots), `entrypoint.sh`.

### No incluye
- UI web, base de datos, persistencia avanzada.
- Tracking / reidentificación, grabación de video.
- Zonas de interés (ROI), tests automatizados.

## Requisitos

1. Leer config desde `config.yaml` (PyYAML).
2. Inicializar MQTT y YOLO compartidos antes de lanzar threads.
3. Por cada cámara, leer frames en loop y procesar 1 de cada N (`process_every_n_frames`).
4. Filtrar detecciones por `classes_to_detect` y `confidence_threshold`.
5. Al detectar, aplicar cooldown por `camera:clase`; si pasa, guardar snapshot y publicar MQTT.
6. Reconectar automáticamente si el RTSP o el MQTT se caen, logueando el evento.
7. Cierre limpio de todos los threads ante señal de terminación.

## Criterios de aceptación

- [x] La app levanta con `python main.py` y un `config.yaml` válido.
- [x] Detecta `person` y publica el payload MQTT esperado con `image_url`.
- [x] Respeta el cooldown configurado (no hace spam de mensajes).
- [x] Se reconecta sola si se cae el stream o el broker.
- [x] Corre en Docker vía `docker compose up -d`.

## Payload MQTT

```json
{
  "event": "person_detected",
  "camera": "cochera",
  "confidence": 0.83,
  "timestamp": "2026-03-16T00:00:00Z",
  "image_url": "http://IP:8081/snapshots/cochera/cochera_20260316_035213.jpg"
}
```

Los campos se controlan vía la sección `publish:` de la config (`include_bbox`, etc.).

## Arquitectura

Ver [CLAUDE.md](../../CLAUDE.md#arquitectura) para el detalle de módulos y el modelo mental
del flujo. Componentes: `main.camera_loop`, `YoloDetector`, `RTSPReader`, `MQTTClient`,
`CooldownRateLimiter`, `save_snapshot`, `get_logger`.

## Deuda conocida / mejoras candidatas

Insumos para próximos specs (no implementados en el baseline):

- El config soporta `mqtt_topic` por cámara, pero `camera_loop` publica al topic global (`mqtt.topic`); el campo por cámara queda sin usar.
- No hay tests automatizados.
- `build_payload` recibe un `cfg_wrapper` ad-hoc; se podría simplificar la firma.
- Sin health-check ni métricas.
- Soporte multi-clase (`car`, `dog`) y zonas de interés (ROI) pendientes.
