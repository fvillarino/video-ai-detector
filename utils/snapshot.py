from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


def save_snapshot(
    frame: np.ndarray,
    camera_name: str,
    snapshots_path: str,
    base_url: str,
) -> str | None:
    """
    Guarda el frame como JPEG en snapshots_path/{camera_name}/.
    Retorna la URL pública de la imagen, o None si falla.
    """
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{camera_name}_{ts}.jpg"

        cam_dir = Path(snapshots_path) / camera_name
        cam_dir.mkdir(parents=True, exist_ok=True)

        file_path = cam_dir / filename
        cv2.imwrite(str(file_path), frame)

        url = f"{base_url.rstrip('/')}/{camera_name}/{filename}"
        logger.debug(f"Snapshot guardado: {file_path}")
        return url

    except Exception as exc:
        logger.warning(f"No se pudo guardar snapshot: {exc}")
        return None
