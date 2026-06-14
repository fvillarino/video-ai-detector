from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from ultralytics import YOLO

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2


class YoloDetector:
    def __init__(
        self,
        model_path: str,
        classes_to_detect: list[str],
        confidence_threshold: float = 0.5,
        image_size: int = 640,
    ):
        logger.info(f"Cargando modelo YOLO: {model_path}")
        self.model = YOLO(model_path)
        self.classes_to_detect = set(classes_to_detect)
        self.confidence_threshold = confidence_threshold
        self.image_size = image_size
        logger.info(f"Modelo listo. Clases a detectar: {self.classes_to_detect}")

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model.predict(
            source=frame,
            imgsz=self.image_size,
            conf=self.confidence_threshold,
            verbose=False,
        )

        detections: list[Detection] = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                if class_name not in self.classes_to_detect:
                    continue
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
                detections.append(
                    Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2),
                    )
                )
        return detections
