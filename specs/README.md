# Specs — Spec-Driven Development

Esta carpeta contiene los specs del proyecto. Cada cambio no trivial (feature nuevo,
refactor grande, cambio de comportamiento) se diseña acá **antes** de escribir código.

## Por qué

Pensar primero en el *qué* y el *por qué*, después en el *cómo*, y recién después
codear. Así los cambios quedan documentados, son revisables y Claude Code (o cualquier
persona) puede retomarlos con contexto completo.

## Estructura

Cada spec es una carpeta numerada:

```
specs/
├── README.md                  (este archivo)
├── _templates/                (plantillas para copiar)
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 000-baseline/              (estado actual de la POC, ya implementado)
│   └── spec.md
└── NNN-nombre-corto/          (un feature por carpeta)
    ├── spec.md                (el QUÉ y el POR QUÉ)
    ├── plan.md                (el CÓMO técnico)
    └── tasks.md               (pasos accionables)
```

`NNN` es un número incremental de 3 dígitos (001, 002, ...). `nombre-corto` en kebab-case.

## Flujo

1. **Crear la carpeta** `specs/NNN-nombre-corto/` y copiar las plantillas de `_templates/`.
2. **spec.md** — definir problema, objetivo, requisitos y criterios de aceptación.
   Acordarlo con el usuario antes de seguir. Sin detalles de implementación.
3. **plan.md** — diseñar el enfoque técnico: archivos a tocar, cambios de config, riesgos.
4. **tasks.md** — desglosar en pasos chicos, ordenados y verificables.
5. **Implementar** — escribir código siguiendo las tasks, marcándolas a medida que se completan.
6. **Cerrar** — actualizar los artefactos si la implementación se desvió del plan, y
   marcar el spec como `Estado: Implementado`.

## Estados de un spec

Indicar en el encabezado del `spec.md`:

- `Borrador` — en discusión, todavía no acordado.
- `Aprobado` — acordado, listo para planificar/implementar.
- `En progreso` — implementación en curso.
- `Implementado` — completo y en `main`.
- `Descartado` — se decidió no hacerlo (dejar nota del por qué).

## Reglas

- Specs triviales (fix de una línea, typo) no necesitan carpeta; se hacen directo.
- Un spec describe **un** cambio coherente. Si crece demasiado, partirlo.
- Mantener los artefactos como documentación viva: si cambia el alcance, actualizar el spec.
