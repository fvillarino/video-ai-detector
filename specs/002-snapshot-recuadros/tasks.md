# Tasks 002 — Recuadros de detección en el snapshot

Pasos para implementar [plan.md](plan.md). Marcar a medida que se completan.

- [x] 1. `utils/snapshot.py`: helper `_draw_detections` + nuevos params `detections` / `draw_detections` en `save_snapshot`.
- [x] 2. `main.py`: pasar `detections` y `draw_detections` (de `snap_cfg`) en la llamada a `save_snapshot`.
- [x] 3. `config.yaml.example`: agregar `draw_detections: true` bajo `snapshots:`.
- [x] 4. `requirements-dev.txt`: agregar `pytest`.
- [x] 5. `tests/test_snapshot.py`: tests del dibujado (flag on/off, archivo generado).
- [x] 6. Correr `pytest` y verificar que pasa (4 passed).
- [x] 7. Actualizar `README.md` / `CLAUDE.md`: nuevo flag y cómo correr los tests.
- [ ] 8. Verificación manual con una imagen real (opcional, usuario, contra cámara/HA).

## Notas de implementación

- Estilo fijo: caja verde BGR (0,200,0) grosor 2; etiqueta blanca sobre fondo verde.
- Duck typing en `save_snapshot` (sin importar `Detection` en runtime); anotación con `TYPE_CHECKING`.
