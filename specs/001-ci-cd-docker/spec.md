# Spec 001 — CI/CD de imagen Docker

- **Estado:** Implementado
- **Autor:** Federico Villarino
- **Fecha:** 2026-06-14

## Problema

Hoy la imagen Docker se buildea **a mano** en la máquina Windows de desarrollo (`make build`)
y se sube manualmente a DockerHub (`make push`). Esto tiene tres problemas:

1. La imagen depende del entorno local (no es reproducible; "anda en mi máquina").
2. El flujo es manual y fácil de olvidar o hacer mal.
3. Solo existe el tag `latest`: no hay forma clara de saber qué versión corre en el
   Beelink ni de hacer rollback a una versión anterior.

## Objetivo

Que cada release publique automáticamente una imagen Docker **versionada y reproducible**
en un registry, y que actualizar el Beelink sea un comando explícito y seguro.

## Alcance

### Incluye
- Workflow de GitHub Actions que buildea y pushea la imagen en cada **git tag** `v*`.
- Publicación en **GHCR** (`ghcr.io/fvillarino/video-ai-detector`), autenticado con `GITHUB_TOKEN`.
- Tags de imagen: la versión del git tag (`v1.0.1`), el short SHA del commit, y `latest`.
- Build **single-arch linux/amd64** (el Beelink es x86_64 / amd64).
- Actualizar `docker-compose.yml` para apuntar a GHCR.
- Script/target de deploy manual en el Beelink (`pull` + `up -d` de una versión fija).
- Documentar el flujo de release y deploy en README/CLAUDE.

### No incluye
- Auto-deploy (Watchtower o SSH desde la Action): el deploy queda **manual y explícito**.
- Build multi-arch (no hay targets ARM por ahora).
- Tests en CI (no hay suite todavía; será otro spec).
- Migrar imágenes históricas de DockerHub.

## Requisitos

1. Al pushear un tag de git `vX.Y.Z`, GitHub Actions buildea la imagen y la publica en GHCR.
2. La imagen se etiqueta con: `vX.Y.Z`, el short SHA (ej. `sha-c6956d7`) y `latest`.
3. El push a GHCR usa `GITHUB_TOKEN` (sin secrets de credenciales externas).
4. `docker-compose.yml` referencia `ghcr.io/fvillarino/video-ai-detector` con una **versión fija** (no `latest`).
5. Existe un comando de deploy en el Beelink que hace `docker compose pull && docker compose up -d`.
6. El paquete de GHCR queda **público** (para poder pullear sin login en el Beelink) o se documenta el login.

## Criterios de aceptación

- [ ] Pushear un tag `vX.Y.Z` produce una imagen en `ghcr.io/fvillarino/video-ai-detector` con los 3 tags.
- [ ] El workflow no requiere configurar secrets manuales de registry.
- [ ] En el Beelink, `docker compose pull && up -d` (o el target nuevo) baja y corre la versión fijada.
- [ ] El README documenta cómo cortar un release (taggear) y cómo deployar.
- [ ] El build es `linux/amd64` y la imagen corre en el Beelink sin cambios funcionales.

## Consideraciones

- **Visibilidad del paquete GHCR:** por defecto un package nuevo en GHCR es privado aunque el repo
  sea público; hay que hacerlo público (o loguear el Beelink con un PAT de solo lectura). El spec
  asume público para mantener el `pull` sin credenciales, igual que hoy con DockerHub.
- **Compatibilidad:** el Beelink sigue usando Docker Compose y `network_mode: host`; solo cambia
  el nombre de la imagen y el tag. La migración es cambiar el `image:` y `compose pull && up -d`.
- **Versionado:** la versión vive en el git tag, fuente única de verdad. El `Makefile` actual
  (`VERSION = 1.0.0`) deja de ser quien decide la versión publicada.
- **Riesgo bajo:** no toca la lógica de la app; si el workflow falla, el flujo manual sigue disponible.

## Preguntas resueltas

- **DockerHub:** se corta directo a GHCR; DockerHub queda como histórico. (Acordado 2026-06-14)
- **Deploy:** target `deploy` en el Makefile, consistente con `up`/`down`/`logs`. (Acordado 2026-06-14)
- **Versión a desplegar:** se fija vía `APP_VERSION` en un `.env` del Beelink que lee Compose
  (se provee `.env.example`); así se pinea la versión sin editar el `docker-compose.yml`.
