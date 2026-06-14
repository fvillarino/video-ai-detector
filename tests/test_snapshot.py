"""Tests del guardado de snapshots con recuadros de detección (spec 002)."""

from types import SimpleNamespace

import cv2
import numpy as np

from utils.snapshot import save_snapshot


def _frame() -> np.ndarray:
    # Frame negro: cualquier dibujo deja píxeles > 0.
    return np.zeros((120, 200, 3), dtype=np.uint8)


def _detection():
    # Duck typing: save_snapshot solo necesita .bbox, .class_name, .confidence.
    return SimpleNamespace(class_name="person", confidence=0.83, bbox=(20, 30, 90, 110))


def _saved_image(tmp_path):
    files = list((tmp_path / "cochera").glob("*.jpg"))
    assert len(files) == 1, f"se esperaba 1 snapshot, hay {len(files)}"
    img = cv2.imread(str(files[0]))
    assert img is not None
    return img


def test_dibuja_recuadro_cuando_esta_activo(tmp_path):
    url = save_snapshot(
        _frame(), "cochera", str(tmp_path), "http://x:8081/snapshots",
        detections=[_detection()], draw_detections=True,
    )
    assert url == "http://x:8081/snapshots/cochera/" + url.rsplit("/", 1)[1]
    # Sobre un frame negro, el recuadro + etiqueta deja píxeles distintos de cero.
    assert _saved_image(tmp_path).sum() > 0


def test_no_dibuja_cuando_esta_desactivado(tmp_path):
    save_snapshot(
        _frame(), "cochera", str(tmp_path), "http://x:8081/snapshots",
        detections=[_detection()], draw_detections=False,
    )
    # Sin dibujar, el frame negro se guarda intacto (JPEG de todo-cero sigue en cero).
    assert _saved_image(tmp_path).sum() == 0


def test_no_dibuja_sin_detecciones(tmp_path):
    save_snapshot(
        _frame(), "cochera", str(tmp_path), "http://x:8081/snapshots",
        detections=[], draw_detections=True,
    )
    assert _saved_image(tmp_path).sum() == 0


def test_recuadra_todas_las_detecciones(tmp_path):
    dets = [
        SimpleNamespace(class_name="person", confidence=0.83, bbox=(10, 10, 40, 60)),
        SimpleNamespace(class_name="car", confidence=0.7, bbox=(100, 50, 180, 110)),
    ]
    save_snapshot(
        _frame(), "cochera", str(tmp_path), "http://x:8081/snapshots",
        detections=dets, draw_detections=True,
    )
    img = _saved_image(tmp_path)
    # Hay dibujo en la zona de cada detección.
    assert img[10:60, 10:40].sum() > 0
    assert img[50:110, 100:180].sum() > 0
