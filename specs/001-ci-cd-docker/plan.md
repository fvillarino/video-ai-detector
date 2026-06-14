# Plan 001 — CI/CD de imagen Docker

Plan técnico para implementar [spec.md](spec.md).

## Enfoque

- **Build/publish:** un workflow de GitHub Actions disparado por tags `v*` (y `workflow_dispatch`
  para correr a mano). Usa las acciones oficiales `docker/metadata-action`, `docker/login-action`
  y `docker/build-push-action`, con caché de capas `type=gha`.
- **Auth:** `GITHUB_TOKEN` con permiso `packages: write`. Sin secrets externos.
- **Tags de imagen:** el git tag literal (`v1.0.1`), el short SHA (`sha-xxxxxxx`) y `latest`,
  generados por `metadata-action`.
- **Arquitectura:** solo `linux/amd64` (Beelink x86_64).
- **Versión a desplegar:** Compose lee `APP_VERSION` desde un `.env` (no commiteado) en el Beelink;
  se provee `.env.example`. Así se pinea la versión sin tocar `docker-compose.yml`.
- **Deploy:** target `make deploy` = `docker compose pull && docker compose up -d`.

## Cambios por archivo

| Archivo | Cambio |
|---|---|
| `.github/workflows/docker-publish.yml` | **Nuevo.** Workflow build+push a GHCR en tags `v*`. |
| `docker-compose.yml` | `image:` → `ghcr.io/fvillarino/video-ai-detector:${APP_VERSION:-latest}`. |
| `.env.example` | **Nuevo.** `APP_VERSION=v1.0.0` con comentario. |
| `Makefile` | `IMAGE` → ruta GHCR; nuevo target `deploy`; nota de que CI es el publish principal. |
| `.gitignore` | Asegurar que `.env` esté ignorado (ya lo está) y `.env.example` no. |
| `README.md` | Reemplazar sección "Docker (próxima etapa)" por "Release y deploy". |
| `CLAUDE.md` | Actualizar comandos (GHCR, `make deploy`) y describir el flujo de release. |

## Configuración / archivos nuevos

`.env.example` (el Beelink lo copia a `.env`):

```bash
# Versión publicada en GHCR a desplegar. Cambiá el valor y corré `make deploy`.
APP_VERSION=v1.0.0
```

Tags generados por `metadata-action`:

```
type=ref,event=tag         # v1.0.1
type=sha,prefix=sha-       # sha-c6956d7
type=raw,value=latest      # latest
```

## Alternativas consideradas

- **Auto-deploy (Watchtower / SSH desde la Action):** descartado por el spec — el deploy es manual.
- **Pinear la versión hardcodeada en `docker-compose.yml`:** descartado; obligaría a editar el
  compose en cada release. Se usa `APP_VERSION` vía `.env` en su lugar.
- **Build multi-arch con buildx:** innecesario, el Beelink es amd64.
- **`type=semver,pattern={{version}}`** (tag sin `v`): se prefiere `type=ref,event=tag` para que
  el tag de imagen coincida 1:1 con el git tag (`v1.0.1`).

## Riesgos y mitigaciones

- **Package GHCR nace privado:** tras el primer release hay que marcarlo público en GitHub
  (Packages → settings) para que el Beelink pullee sin login. Documentado en README.
- **Si el workflow falla:** el flujo manual (`make build && make push`, ahora apuntando a GHCR)
  queda disponible como fallback.
- **`.env` ausente en el Beelink:** Compose caería a `latest`; se documenta crear el `.env`.

## Verificación

1. `docker compose config` resuelve la imagen GHCR con la versión esperada (local, con un `.env` de prueba).
2. Pushear un tag de prueba `v0.0.1-test` y confirmar que el workflow publica los 3 tags en GHCR.
3. En el Beelink: marcar el package público, crear `.env`, `make deploy`, verificar que corre.
4. Revisar logs del contenedor: detección y publicación MQTT siguen funcionando.
