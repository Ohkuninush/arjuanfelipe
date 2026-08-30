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
nada más**.

- Host VPS: `158.69.213.49` (usuario `ubuntu`), host key fijado en el workflow.
- Secret requerido: `VPS_DEPLOY_KEY` (clave privada ed25519).
- Webroot de Nginx: `/opt/sites/arjuanfelipe/webroot/`. Cloudflare (proxied,
  Full strict) → VPS. Vhost `/etc/nginx/sites-available/arjuanfelipe.conf`
  con guard `if ($is_cloudflare = 0) { return 403; }`.
- CI verificado operativo el 2026-08-30.

### `deploy.sh` — publica el árbol multipágina (actualizado 2026-08-30)

`/opt/sites/arjuanfelipe/deploy.sh` hace `git fetch` + `reset --hard
origin/main` en `$SITE/repo`, construye un staging con **allowlist**
(`index.html assets applications es work lab cv identity/dist`) y hace
`rsync -a --delete` de staging a `$SITE/webroot`. Backup del script anterior
(sólo `index.html`) en `deploy.sh.bak.20260830`.

Nginx no necesitó cambios: `location / { try_files $uri $uri/ =404; }` +
`index index.html;` ya resuelve `/applications/` → `/applications/index.html`.
No se tocó Nginx/DNS/TLS ni otras apps de `/opt/sites/*`.

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
- [x] COMMIT — `9556a25` (feature + SSG + HTML generado + WDS) + `b4d7b20`
      (docs) en `main`.
- [x] VPS — `deploy.sh` reescrito para publicar el árbol completo; Nginx sin
      cambios.
- [x] PUSH — `git push origin main` hecho; CI `deploy.yml` verde (run
      33340523614).
- [x] VERIFICADO EN VIVO (2026-08-30) — `https://arjuanfelipe.com/`,
      `/applications/`, `/es/applications/`, `/work/`, `/cv/`,
      `/assets/applications/*.svg`, favicon → 200; `/nonexistent/` → 404;
      nav con "Applications"/"Aplicaciones"; GitHub/LinkedIn/tema/idioma
      intactos.
- [x] HTTPS / dominio — sin cambios; operativo.

**En producción.** Para cambios futuros: editar `site/content|core`, rebuild,
commit del HTML regenerado, `git push` → CI despliega.
