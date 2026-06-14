# Spec 002 — Recuadros de detección en el snapshot

- **Estado:** Implementado
- **Autor:** Federico Villarino
- **Fecha:** 2026-06-14

## Problema

El snapshot que se guarda (y se expone en Home Assistant) es el frame **crudo**, sin ninguna
marca visual. Cuando llega la notificación, no se ve **qué** se detectó ni **dónde** en la imagen.
Existe `publish.include_bbox`, pero eso solo agrega las coordenadas al **payload MQTT** (números),
no dibuja nada sobre la imagen.

## Objetivo

Que el snapshot guardado tenga dibujado un recuadro sobre cada objeto detectado, con su clase y
confianza, para identificar de un vistazo qué disparó el evento.

## Alcance

### Incluye
- Dibujar un recuadro por **cada detección** (de las clases configuradas) presente en el frame.
- Cada recuadro muestra una etiqueta con **clase + confianza** (ej. `person 0.83`).
- Nuevo flag de config `snapshots.draw_detections` (default `true`) para activarlo/desactivarlo.
- No alterar el frame original usado por otras partes del loop (dibujar sobre una copia).

### No incluye
- Cambios en el payload MQTT (`include_bbox` sigue igual e independiente).
- Colores por clase configurables, fuentes custom, opacidad, etc. (un color/estilo fijo y legible).
- Guardar además la imagen sin anotar (solo se guarda la anotada cuando el flag está en `true`).
- Zonas de interés (ROI) ni dibujado de otra cosa que no sean las detecciones.

## Requisitos

1. Cuando `snapshots.draw_detections: true`, el JPEG guardado incluye los recuadros de todas las
   detecciones del frame.
2. Cada recuadro lleva una etiqueta legible con clase y confianza (`<clase> <conf>`, ej. `person 0.83`).
3. La etiqueta debe leerse sobre cualquier fondo (texto con fondo de contraste, no texto suelto).
4. Con `snapshots.draw_detections: false`, se guarda el frame crudo (comportamiento actual).
5. Si el flag no está en la config, el comportamiento por defecto es dibujar (`true`).
6. El dibujado no debe modificar el frame que usa el resto del `camera_loop`.

## Criterios de aceptación

- [ ] Con el flag activo, una detección de `person` produce un snapshot con la caja + `person 0.83`.
- [ ] Si hay varias detecciones de clases configuradas en el frame, aparecen todas recuadradas.
- [ ] Con el flag en `false`, el snapshot sale sin recuadros (como hoy).
- [ ] El payload MQTT no cambia respecto del comportamiento actual.
- [ ] `config.yaml.example` documenta el nuevo flag.

## Consideraciones

- **Dependencias:** se usa OpenCV (`cv2.rectangle`, `cv2.putText`), ya presente. Sin libs nuevas.
- **Colores:** OpenCV trabaja en BGR. Se usa un color de acento fijo y legible (a definir en el plan).
- **Performance:** dibujar unas pocas cajas por frame es despreciable; solo ocurre cuando se va a
  guardar un snapshot (es decir, tras pasar el cooldown), no en cada frame.
- **Acoplamiento:** `save_snapshot` necesitará las detecciones. Definir en el plan si recibe la
  lista de `Detection` o una estructura simple (bbox + etiqueta) para no acoplar `utils` a `detector`.
- **Tests:** buen candidato para el primer test con `pytest` (que el dibujado no rompe y respeta el flag).

## Preguntas abiertas

- Ninguna pendiente. Decisiones tomadas: recuadrar **todas** las detecciones del frame; etiqueta
  con **clase + confianza**; **configurable** vía `snapshots.draw_detections` (default `true`).
