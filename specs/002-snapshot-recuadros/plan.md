# Plan 002 — Recuadros de detección en el snapshot

Plan técnico para implementar [spec.md](spec.md).

## Enfoque

El dibujado vive en `utils/snapshot.py`, junto al guardado. `save_snapshot` recibe la lista de
detecciones y un flag `draw_detections`; si está activo, dibuja sobre una **copia** del frame antes
de escribir el JPEG. `main.camera_loop` le pasa la lista completa de detecciones del frame y el flag
desde `snap_cfg`.

## Decisiones de diseño

- **Acoplamiento `utils` → `detector`:** `save_snapshot` NO importa `Detection` en runtime (eso
  arrastraría `ultralytics` al importar `utils`). Se usa **duck typing**: las detecciones solo
  necesitan `.bbox`, `.class_name`, `.confidence`. La anotación de tipo se hace con `TYPE_CHECKING`.
- **Estilo del recuadro (fijo, no configurable):**
  - Caja: verde BGR `(0, 200, 0)`, grosor `2`.
  - Etiqueta `f"{class_name} {confidence:.2f}"` en blanco, sobre un rectángulo relleno verde
    (fondo de contraste) para que se lea sobre cualquier imagen. Fuente `FONT_HERSHEY_SIMPLEX`.
  - La etiqueta se ubica arriba de la caja; si no hay lugar (pegada al borde superior), va dentro.
- **Copia del frame:** se dibuja sobre `frame.copy()` solo cuando hay que dibujar, para no mutar el
  frame que usa el resto del `camera_loop`.

## Cambios por archivo

| Archivo | Cambio |
|---|---|
| `utils/snapshot.py` | `save_snapshot(...)` recibe `detections` y `draw_detections`; helper `_draw_detections`. |
| `main.py` | En `camera_loop`, pasar `detections=detections` y `draw_detections=snap_cfg.get("draw_detections", True)`. |
| `config.yaml.example` | Agregar `draw_detections: true` bajo `snapshots:`. |
| `tests/test_snapshot.py` | **Nuevo.** Tests del dibujado y del flag (estrena pytest). |
| `requirements-dev.txt` | **Nuevo.** `pytest` para correr los tests. |
| `README.md` / `CLAUDE.md` | Documentar el flag y cómo correr los tests. |

## Firma propuesta

```python
def save_snapshot(
    frame: np.ndarray,
    camera_name: str,
    snapshots_path: str,
    base_url: str,
    detections: "Sequence[Detection] | None" = None,
    draw_detections: bool = True,
) -> str | None:
```

`config.yaml.example` (sección `snapshots`):

```yaml
snapshots:
  enabled: true
  path: "snapshots"
  base_url: "http://IP_SERVIDOR:8081/snapshots"
  draw_detections: true   # dibujar recuadro + clase/confianza sobre el snapshot
```

## Alternativas consideradas

- **Importar `Detection` en `utils/snapshot.py`:** descartado, arrastra `ultralytics` al importar utils.
- **Pasar `list[tuple[bbox, label]]` en vez de detecciones:** válido, pero duck-typing con los
  atributos de `Detection` es más directo y no obliga a construir tuplas en `camera_loop`.
- **Dibujar en el `YoloDetector`:** mezcla inferencia con presentación; mejor mantenerlo en snapshot.

## Riesgos y mitigaciones

- **Etiqueta ilegible / fuera de la imagen:** se usa fondo de contraste y se clampea la posición.
- **Mutación del frame compartido:** se dibuja sobre una copia.
- **Coordenadas fuera de rango:** OpenCV recorta solo; las bbox vienen de YOLO dentro del frame.

## Verificación

- `pytest` pasa: snapshot con `draw_detections=True` difiere del frame crudo; con `False` no dibuja.
- Prueba manual con la imagen real: el JPEG guardado muestra la caja sobre la persona con `person 0.xx`.
- El payload MQTT no cambia.
