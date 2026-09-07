# arjuanfelipe.com

Sitio personal de Juan Felipe — QA · Data · Ingeniería.
Estático (HTML + CSS + JS), bilingüe EN/ES, sin build, desplegado en VPS propio.

```
index.html                 home (EN)
es/index.html              home (ES)
assets/site.css            estilos (tema único)
assets/site.js             terminal animada
notes/                     notas / blog (EN)
es/notes/                  notas / blog (ES)
```

## Editar

Todo es HTML plano. No hay generador ni framework.

- Contenido de la home: `index.html` y `es/index.html`.
- Nueva nota: crear `notes/<slug>/index.html` (copiar una existente),
  añadir la línea en `notes/index.html` y su espejo en `es/`.

## Deploy

Ver [`DEPLOY.md`](DEPLOY.md). Push a `main` → GitHub Actions → SSH al VPS.
