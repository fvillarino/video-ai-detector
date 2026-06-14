# Tasks 001 — CI/CD de imagen Docker

Pasos para implementar [plan.md](plan.md). Marcar a medida que se completan.

- [x] 1. Crear `.github/workflows/docker-publish.yml` (build+push a GHCR en tags `v*` + `workflow_dispatch`).
- [x] 2. Actualizar `docker-compose.yml`: `image:` → `ghcr.io/fvillarino/video-ai-detector:${APP_VERSION:-latest}`.
- [x] 3. Crear `.env.example` con `APP_VERSION=v1.0.0`.
- [x] 4. Actualizar `Makefile`: `IMAGE` a ruta GHCR + nuevo target `deploy` + nota sobre CI.
- [x] 5. Actualizar `README.md`: reemplazar "Docker (próxima etapa)" por "Release y deploy".
- [x] 6. Actualizar `CLAUDE.md`: comandos (GHCR, `make deploy`) y flujo de release.
- [x] 7. Verificar local: `docker compose config` resuelve la imagen y versión correctas.
- [ ] 8. (Manual, usuario) Cortar primer release: `git tag v1.0.0 && git push origin v1.0.0`, confirmar workflow en GHCR.
- [ ] 9. (Manual, usuario) Marcar el package GHCR como público.
- [ ] 10. (Manual, usuario) En el Beelink: crear `.env`, `make deploy`, verificar logs.

## Notas de implementación

- Tags de imagen vía `metadata-action`: `type=ref,event=tag`, `type=sha,prefix=sha-`, `type=raw,value=latest`.
- Pasos 8–10 son acciones del usuario (requieren push de tag real y acceso al Beelink); se documentan en README.
