# Deploy — arjuanfelipe.com

Sitio **estático**. Sin build, sin runtime, sin dependencias. El servidor web
sirve archivos desde el webroot del sitio en el VPS.

## Publicar

Un push a `main` que toque `index.html`, `assets/**`, `notes/**` o `es/**`
dispara `.github/workflows/deploy.yml`:

1. GitHub Actions abre SSH al host de deploy (host key fijado) con una clave
   dedicada de un usuario sin privilegios cuyo `authorized_keys` fuerza
   `command=` al script de publicación — la clave no puede ejecutar nada más.
2. El script hace `git fetch` + `reset --hard origin/main` en el clon del repo
   y publica con `rsync -a --delete` al webroot.

**Secrets requeridos:** `VPS_DEPLOY_KEY`, `VPS_DEPLOY_HOST`, `VPS_DEPLOY_USER`,
`VPS_DEPLOY_HOSTKEY` (Settings → Secrets and variables → Actions).

## Allowlist del script de publicación (en el VPS)

El staging que se sincroniza al webroot debe ser:

```
index.html assets notes es
```

(Antes incluía `applications work lab cv identity/dist`; esas rutas ya no
existen en el repo.)

## No se toca

Configuración del servidor web, DNS, TLS, ni ninguna otra aplicación del VPS.
El deploy corre como un usuario dedicado sin `sudo`, con acceso solo al árbol
de este sitio.
