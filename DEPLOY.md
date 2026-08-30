# Despliegue — arjuanfelipe.com

## Qué es este proyecto

Sitio **estático**, generado por un SSG propio en Python. No hay servidor de
aplicación, ni Node en runtime, ni base de datos. El output es HTML + CSS + un
JS pequeño, servible por cualquier servidor de archivos.

```
identity/  ──►  wds/  ──►  site/  ──►  HTML en la raíz del repo
(glyph CDS)   (design     (build       (index.html, es/, work/, lab/,
              system)     del sitio)    cv/, applications/, assets/)
```

### Build local

```bash
python wds/build_wds.py       # compila wds/css/*.css  (design system)
python site/build_site.py     # genera todo el HTML + assets/site.{css,js}
python site/validate_site.py  # 31 checks estructurales — deben pasar
python wds/validate_wds.py    # 20 checks del design system
```

`build_site.py` **regenera** `index.html` y los subdirectorios de páginas. No
editar el HTML a mano: el contenido vive en `site/content/*.py` y la
composición en `site/core/*.py`.

- Requiere: Python 3.11 (sólo stdlib, sin dependencias externas — no hay
  `requirements.txt` ni lockfile).
- No hay `package.json`, no hay config de Vercel, no hay variables de entorno.

### Preview local

```bash
python site/devserver.py 8123   # http://localhost:8123  (sin caché)
```

---

## Despliegue actual (CI → VPS)

`.github/workflows/deploy.yml`: cada push a `main` que toque rutas del sitio
abre SSH al VPS con una clave dedicada cuyo `authorized_keys` fuerza
`command="/opt/sites/arjuanfelipe/deploy.sh"`. Esa clave **no puede ejecutar
nada más**. `deploy.sh` (vive en el VPS, no en el repo) hace `git fetch` +
`git reset --hard origin/main` y publica en el webroot de Nginx.

- Host VPS: `158.69.213.49` (usuario `ubuntu`), host key fijado en el workflow.
- Secret requerido: `VPS_DEPLOY_KEY` (clave privada ed25519 `arjuanfelipe_ci`).
- No toca Nginx, DNS, TLS ni otras apps del VPS.
- Rollback de emergencia: revertir DNS en Cloudflare a Vercel
  (A apex `76.76.21.21`, CNAME www `cname.vercel-dns.com`).

### ⚠️ Pendiente de verificar en el VPS antes de confiar el multipágina

El comentario de `deploy.yml` dice que `deploy.sh` "publica **index.html** en
el webroot". Hasta hoy el sitio en producción era **un solo `index.html`**. El
sitio multipágina (subdirectorios + `/assets/`) **nunca se ha desplegado**.
Antes del primer push que lo incluya, confirmar por SSH en el VPS:

1. `cat /opt/sites/arjuanfelipe/deploy.sh` — ¿copia sólo `index.html`, o
   sincroniza todo el árbol / apunta el webroot al checkout de git?
2. `ls -la` del webroot de Nginx para `arjuanfelipe.com` (¿es el checkout de
   git, o un directorio aparte al que `deploy.sh` copia archivos?).
3. `cat` del `server {}` de Nginx del sitio: `root`, `index`,
   `try_files $uri $uri/ =404;` (necesario para que `/applications/` resuelva
   a `/applications/index.html`).
4. Que el usuario del deploy pueda escribir el webroot y recargar Nginx sin
   pisar otras apps (`/opt/sites/*` es multi-proyecto).

Si `deploy.sh` sólo copia `index.html`: hay que ampliarlo (o cambiar el
webroot al checkout) **en el VPS**, no en este repo.

---

## Requisitos para servir en el VPS (resumen)

| Aspecto | Necesidad |
|---|---|
| Proceso runtime | Ninguno. Archivos estáticos. |
| Puerto propio | No. Lo sirve el Nginx ya existente como otro `server {}`/root. |
| Node.js | No en runtime. |
| Build previo | Sí: `python wds/build_wds.py && python site/build_site.py`. Hoy el output se commitea al repo, así que el VPS sólo hace checkout (no build). |
| Sitio estático | Sí, 100%. |
| Proceso persistente | No. |
| Config Nginx | `root` al directorio publicado; `index index.html;`; `try_files $uri $uri/ /404.html;` o `=404`; `location = /es/ { }` etc. funcionan solos con `$uri/`. Cabeceras recomendadas: `Cache-Control` corto para `*.html`, largo + immutable para `/assets/*` (llevan `?v=hash`). |
| Variables de entorno | Ninguna. |
| Certificados / dominio | `arjuanfelipe.com` + `www` ya en Cloudflare → VPS. TLS lo maneja la infra existente del VPS (Let's Encrypt/Cloudflare). No cambia. |
| Dependencias del VPS | Python 3.11 sólo si se quiere buildear en el VPS; si se sigue commiteando el output, ni eso. |

## Estado: LOCAL → BUILD → VPS → Nginx → HTTPS → arjuanfelipe.com

- [x] LOCAL — sección *Applications / Aplicaciones* implementada sobre el SSG.
- [x] BUILD — `site/build_site.py` OK (20 páginas), `validate_site.py` 31/31,
      `wds` 20/20.
- [ ] Commit + push a `main` — **no ejecutado automáticamente** (el push
      dispara el deploy a producción).
- [ ] VPS — `deploy.sh` / webroot / Nginx `try_files` **sin verificar** (sin
      acceso SSH desde aquí). Ver checklist arriba.
- [ ] HTTPS / dominio — sin cambios; ya operativo.

**No está "en producción".** Falta: (1) verificar el VPS, (2) `git push
origin main`, (3) comprobar que `/applications/` y `/es/applications/`
resuelven y que GitHub/LinkedIn/Work/Lab/CV siguen intactos en el sitio vivo.
