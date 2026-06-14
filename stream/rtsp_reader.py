import time
import cv2
import numpy as np
from typing import Generator

from utils.logger import get_logger

logger = get_logger(__name__)


class RTSPReader:
    def __init__(self, rtsp_url: str, reconnect_delay: int = 5, frame_skip: int = 2):
        self.rtsp_url = rtsp_url
        self.reconnect_delay = reconnect_delay
        self.frame_skip = frame_skip
        self._cap: cv2.VideoCapture | None = None

    def _connect(self) -> bool:
        logger.info("Conectando al stream RTSP...")
        self._cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        if self._cap.isOpened():
            logger.info("Conexión RTSP establecida.")
            return True
        logger.warning("No se pudo abrir el stream RTSP.")
        self._cap.release()
        self._cap = None
        return False

    def frames(self) -> Generator[np.ndarray, None, None]:
        """Generador infinito de frames. Reconecta si el stream se cae."""
        frame_counter = 0
        while True:
            if self._cap is None or not self._cap.isOpened():
                if not self._connect():
                    logger.warning(
                        f"Reintentando conexión en {self.reconnect_delay}s..."
                    )
                    time.sleep(self.reconnect_delay)
                    continue

            ret, frame = self._cap.read()
            if not ret:
                logger.warning("Frame inválido. Se perdió la conexión RTSP.")
                self._cap.release()
                self._cap = None
                time.sleep(self.reconnect_delay)
                continue

            frame_counter += 1
            if frame_counter % (self.frame_skip + 1) != 0:
                continue

            yield frame

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None
