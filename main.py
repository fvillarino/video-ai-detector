"""
Punto de entrada principal — soporte multi-cámara.

Flujo:
  1. Leer configuración desde config.yaml
  2. Inicializar cliente MQTT compartido
  3. Cargar modelo YOLO (compartido entre threads)
  4. Lanzar un thread de captura/detección por cámara
  5. Esperar señal de cierre y terminar limpiamente
"""

import signal
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from detector.yolo_detector import YoloDetector
from messaging.mqtt_client import MQTTClient
from stream.rtsp_reader import RTSPReader
from utils.logger import get_logger
from utils.rate_limit import CooldownRateLimiter
from utils.snapshot import save_snapshot


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def build_payload(
    cfg: dict,
    camera_name: str,
    class_name: str,
    confidence: float,
    bbox: tuple,
    image_url: str | None = None,
) -> dict:
    pub = cfg.get("publish", {})
    payload: dict = {"event": f"{class_name}_detected"}

    if pub.get("include_camera_name", True):
        payload["camera"] = camera_name
    if pub.get("include_confidence", True):
        payload["confidence"] = round(confidence, 4)
    if pub.get("include_timestamp", True):
        payload["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if pub.get("include_bbox", False):
        payload["bbox"] = {"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]}
    if pub.get("include_image_url", True) and image_url:
        payload["image_url"] = image_url

    return payload


def camera_loop(
    cam_cfg: dict,
    det_cfg: dict,
    detector: YoloDetector,
    mqtt_client: MQTTClient | None,
    mqtt_topic: str,
    pub_cfg: dict,
    snap_cfg: dict,
    stop_event: threading.Event,
) -> None:
    camera_name = cam_cfg.get("name", "camera")
    topic = mqtt_topic
    process_every = det_cfg.get("process_every_n_frames", 3)
    logger = get_logger(f"camera.{camera_name}")
    limiter = CooldownRateLimiter(cooldown_seconds=det_cfg["cooldown_seconds"])

    reader = RTSPReader(
        rtsp_url=cam_cfg["rtsp_url"],
        reconnect_delay=cam_cfg.get("reconnect_delay_seconds", 5),
        frame_skip=cam_cfg.get("frame_skip", 2),
    )

    logger.info(f"Iniciando loop de captura.")
    frame_index = 0

    try:
        for frame in reader.frames():
            if stop_event.is_set():
                break

            frame_index += 1
            if frame_index % process_every != 0:
                continue

            detections = detector.detect(frame)

            for det in detections:
                rate_key = f"{camera_name}:{det.class_name}"
                if not limiter.allow(rate_key):
                    continue

                logger.info(
                    f"[{camera_name}] {det.class_name} detectado "
                    f"(conf={det.confidence:.2f}, bbox={det.bbox})"
                )

                image_url: str | None = None
                if snap_cfg.get("enabled", False):
                    image_url = save_snapshot(
                        frame,
                        camera_name,
                        snap_cfg["path"],
                        snap_cfg["base_url"],
                    )

                if mqtt_client:
                    cfg_wrapper = {"publish": pub_cfg}
                    payload = build_payload(cfg_wrapper, camera_name, det.class_name, det.confidence, det.bbox, image_url)
                    mqtt_client.publish(topic, payload)
    finally:
        reader.release()
        logger.info(f"Loop de cámara '{camera_name}' finalizado.")


def main() -> None:
    cfg = load_config()

    log_level = cfg.get("app", {}).get("log_level", "INFO")
    logger = get_logger("main", log_level)
    logger.info(f"Iniciando {cfg.get('app', {}).get('name', 'camera-ai')}")

    # --- MQTT ---
    mqtt_cfg = cfg["mqtt"]
    mqtt_client: MQTTClient | None = None
    if mqtt_cfg.get("enabled", True):
        mqtt_client = MQTTClient(
            host=mqtt_cfg["host"],
            port=mqtt_cfg["port"],
            client_id=f"{mqtt_cfg.get('client_id_prefix', 'camera-ai')}-{uuid.uuid4().hex[:6]}",
            username=mqtt_cfg.get("username"),
            password=mqtt_cfg.get("password"),
        )
        if not mqtt_client.connect():
            logger.warning("La app continuará sin publicar en MQTT.")
            mqtt_client = None

    # --- Detector compartido ---
    det_cfg = cfg["detection"]
    Path("models").mkdir(exist_ok=True)

    detector = YoloDetector(
        model_path=det_cfg["model"],
        classes_to_detect=det_cfg["classes_to_detect"],
        confidence_threshold=det_cfg["confidence_threshold"],
        image_size=det_cfg["image_size"],
    )

    pub_cfg = cfg.get("publish", {})
    snap_cfg = cfg.get("snapshots", {"enabled": False})
    mqtt_topic = mqtt_cfg.get("topic", "cameras/detections")

    if snap_cfg.get("enabled", False):
        Path(snap_cfg["path"]).mkdir(parents=True, exist_ok=True)
        logger.info(f"Snapshots habilitados en: {snap_cfg['path']}")

    # --- Graceful shutdown ---
    stop_event = threading.Event()

    def _shutdown(sig, frame):
        logger.info("Señal de cierre recibida. Finalizando...")
        stop_event.set()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # --- Lanzar un thread por cámara ---
    cameras = cfg.get("cameras", [])
    if not cameras:
        logger.error("No hay cámaras configuradas en 'cameras:'. Revisá config.yaml.")
        sys.exit(1)

    threads: list[threading.Thread] = []
    for cam_cfg in cameras:
        t = threading.Thread(
            target=camera_loop,
            args=(cam_cfg, det_cfg, detector, mqtt_client, mqtt_topic, pub_cfg, snap_cfg, stop_event),
            name=f"cam-{cam_cfg.get('name', 'unknown')}",
            daemon=True,
        )
        t.start()
        threads.append(t)
        logger.info(f"Thread iniciado para cámara '{cam_cfg.get('name')}'.")

    # Esperar a que todos los threads terminen
    for t in threads:
        t.join()

    # --- Cleanup ---
    if mqtt_client:
        mqtt_client.disconnect()
    logger.info("Aplicación terminada.")
    sys.exit(0)


if __name__ == "__main__":
    main()
