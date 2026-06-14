from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

import cv2
import numpy as np

from utils.logger import get_logger

if TYPE_CHECKING:
    from detector.yolo_detector import Detection

logger = get_logger(__name__)

# Estilo fijo del recuadro (OpenCV usa BGR).
_BOX_COLOR = (0, 200, 0)
_TEXT_COLOR = (255, 255, 255)
_FONT = cv2.FONT_HERSHEY_SIMPLEX
_FONT_SCALE = 0.6
_FONT_THICKNESS = 1
_BOX_THICKNESS = 2


def _draw_detections(image: np.ndarray, detections: Sequence["Detection"]) -> None:
    """Dibuja un recuadro con etiqueta (clase + confianza) por cada detección, in-place."""
    for det in detections:
        x1, y1, x2, y2 = (int(v) for v in det.bbox)
        cv2.rectangle(image, (x1, y1), (x2, y2), _BOX_COLOR, _BOX_THICKNESS)

        label = f"{det.class_name} {det.confidence:.2f}"
        (text_w, text_h), baseline = cv2.getTextSize(label, _FONT, _FONT_SCALE, _FONT_THICKNESS)

        # Etiqueta arriba de la caja; si no entra (pegada al borde superior), va dentro.
        label_bottom = y1 if y1 - text_h - baseline - 4 >= 0 else y1 + text_h + baseline + 4
        label_top = label_bottom - text_h - baseline - 4

        cv2.rectangle(image, (x1, label_top), (x1 + text_w + 4, label_bottom), _BOX_COLOR, -1)
        cv2.putText(
            image,
            label,
            (x1 + 2, label_bottom - baseline - 2),
            _FONT,
            _FONT_SCALE,
            _TEXT_COLOR,
            _FONT_THICKNESS,
            cv2.LINE_AA,
        )


def save_snapshot(
    frame: np.ndarray,
    camera_name: str,
    snapshots_path: str,
    base_url: str,
    detections: Sequence["Detection"] | None = None,
    draw_detections: bool = True,
) -> str | None:
    """
    Guarda el frame como JPEG en snapshots_path/{camera_name}/.
    Si draw_detections es True y hay detecciones, dibuja los recuadros sobre una copia
    del frame (no modifica el original). Retorna la URL pública de la imagen, o None si falla.
    """
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_name}_{ts}.jpg"

        cam_dir = Path(snapshots_path) / camera_name
        cam_dir.mkdir(parents=True, exist_ok=True)

        image = frame
        if draw_detections and detections:
            image = frame.copy()
            _draw_detections(image, detections)

        file_path = cam_dir / filename
        cv2.imwrite(str(file_path), image)

        url = f"{base_url.rstrip('/')}/{camera_name}/{filename}"
        logger.debug(f"Snapshot guardado: {file_path}")
        return url

    except Exception as exc:
        logger.warning(f"No se pudo guardar snapshot: {exc}")
        return None
