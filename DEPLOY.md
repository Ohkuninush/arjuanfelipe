# Deploy — arjuanfelipe.com

Sitio **estático**. Sin build, sin runtime, sin dependencias. Nginx sirve
archivos desde `/opt/sites/arjuanfelipe/webroot` en el VPS.

## Publicar

Un push a `main` que toque `index.html`, `assets/**`, `notes/**` o `es/**`
dispara `.github/workflows/deploy.yml`:

1. GitHub Actions abre SSH al VPS (`ubuntu@158.69.213.49`, host key fijado)
   con una clave dedicada cuyo `authorized_keys` fuerza
   `command="/opt/sites/arjuanfelipe/deploy.sh"` — la clave no puede ejecutar
   nada más.
2. `deploy.sh` hace `git fetch` + `reset --hard origin/main` en
   `/opt/sites/arjuanfelipe/repo` y publica con `rsync -a --delete` a `webroot`.

**Secret requerido:** `VPS_DEPLOY_KEY` (clave privada ed25519).

## Allowlist de `deploy.sh` (en el VPS)

El staging que `deploy.sh` sincroniza debe ser:

```
index.html assets notes es
```

(Antes incluía `applications work lab cv identity/dist`; esas rutas ya no
existen en el repo.)

## No se toca

Vhost de Nginx, DNS de Cloudflare, TLS, ni las otras apps de `/opt/sites/*`
(`kaizen`, `colorimetria`, `julymelisa`, `wom`). WOM se sigue sirviendo en
`arjuanfelipe.com/applications/wom/` vía un `alias` de Nginx a
`/opt/sites/wom/webroot`, independiente de este `webroot`.
