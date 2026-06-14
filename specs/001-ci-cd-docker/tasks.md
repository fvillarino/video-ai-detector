# Tasks 001 — CI/CD de imagen Docker

Pasos para implementar [plan.md](plan.md). Marcar a medida que se completan.

- [x] 1. Crear `.github/workflows/docker-publish.yml` (build+push a GHCR en tags `v*` + `workflow_dispatch`).
- [x] 2. Actualizar `docker-compose.yml`: `image:` → `ghcr.io/fvillarino/video-ai-detector:${APP_VERSION:-latest}`.
- [x] 3. Crear `.env.example` con `APP_VERSION=v1.0.0`.
- [x] 4. Actualizar `Makefile`: `IMAGE` a ruta GHCR + nuevo target `deploy` + nota sobre CI.
- [x] 5. Actualizar `README.md`: reemplazar "Docker (próxima etapa)" por "Release y deploy".
- [x] 6. Actualizar `CLAUDE.md`: comandos (GHCR, `make deploy`) y flujo de release.
- [x] 7. Verificar local: `docker compose config` resuelve la imagen y versión correctas.
- [x] 8. Cortar primer release: tag `v1.0.0` pusheado, workflow verde (2m46s), imagen publicada en GHCR con tags v1.0.0 / sha-5a52e6f / latest.
- [x] 9. Marcar el package GHCR como público (hecho por el usuario).
- [ ] 10. (Manual, usuario) En el Beelink: re-apuntar `image:` a GHCR, `docker compose pull && up -d`, verificar logs.

## Notas de implementación

- Tags de imagen vía `metadata-action`: `type=ref,event=tag`, `type=sha,prefix=sha-`, `type=raw,value=latest`.
- **El Beelink NO tiene el repo clonado**: usa un `docker-compose.yml` suelto. El deploy real es
  editar la línea `image:` a `ghcr.io/fvillarino/video-ai-detector:<tag>` + `docker compose pull && up -d`.
  El `.env`/`APP_VERSION` y `make deploy` del repo aplican solo a deploys basados en checkout del repo.
- Task 10 queda pendiente de que el usuario lo corra en el server; no requiere más cambios de código.
