import json
import threading

import paho.mqtt.client as mqtt

from utils.logger import get_logger

logger = get_logger(__name__)


class MQTTClient:
    def __init__(
        self,
        host: str,
        port: int,
        client_id: str,
        username: str | None = None,
        password: str | None = None,
    ):
        self._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        if username:
            self._client.username_pw_set(username, password)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        # Esperar entre 1 y 5 segundos antes de reconectar automáticamente
        self._client.reconnect_delay_set(min_delay=1, max_delay=5)

        self._host = host
        self._port = port
        self._lock = threading.Lock()
        self._connected = False

    def connect(self) -> bool:
        logger.info(f"Conectando a MQTT {self._host}:{self._port}...")
        try:
            self._client.connect(self._host, self._port, keepalive=60)
            self._client.loop_start()
            return True
        except (OSError, TimeoutError) as exc:
            logger.error(f"No se pudo conectar a MQTT: {exc}")
            return False

    def publish(self, topic: str, payload: dict) -> None:
        if not self._connected:
            logger.warning("MQTT no conectado, evento descartado.")
            return
        message = json.dumps(payload)
        with self._lock:
            result = self._client.publish(topic, message, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.warning(f"Error al publicar en MQTT (rc={result.rc})")
        else:
            logger.debug(f"Publicado en {topic}: {message}")

    def disconnect(self) -> None:
        if self._connected:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def _on_connect(self, client, userdata, flags, rc: int) -> None:
        if rc == 0:
            self._connected = True
            logger.info("MQTT conectado correctamente.")
        else:
            self._connected = False
            logger.error(f"Error de conexión MQTT (rc={rc})")

    def _on_disconnect(self, client, userdata, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning(f"Desconexión inesperada de MQTT (rc={rc}). Reconectando...")
