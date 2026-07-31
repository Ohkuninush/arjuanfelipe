# Guía de producción — Identity Production System

## Ejecutar

```bash
python build.py            # pipeline completo: niveles 0 a 5
python verify_formats.py   # re-parsea cada binario con parsers independientes
```

Ambos salen con código 0 en un release limpio. Sin dependencias externas: solo
la biblioteca estándar de Python 3.

## Arquitectura

Seis niveles. El orden es inmutable y las dependencias solo fluyen hacia abajo.

```
LEVEL 0  cds.json              fuente de verdad, única autoridad
LEVEL 1  levels/l1_generate    geometría canónica + másteres
LEVEL 2  levels/l2_validate    mide, nunca modifica. Detiene el pipeline
LEVEL 3  levels/l3_optimize    variantes de producción, presupuesto de error
LEVEL 4  levels/l4_targets     entregables por plataforma
LEVEL 5  levels/l5_qa          QA, hashes, release
```

Ningún nivel puede saltarse otro. Ningún activo generado puede volver a entrar
como entrada de un nivel anterior. El nivel 1 aborta si la geometría
reconstruida no coincide con los literales congelados del CDS, de modo que es
imposible emitir activos desde un CDS incoherente.

## Estructura del repositorio

```
ips/
  cds.json          LEVEL 0 — lo único autoritativo
  CDS.md            especificación normativa legible
  core/
    geometry.py     construcción, Bézier, rasterizado
    svgkit.py       variantes SVG, contorno, minificado, validación
    formats.py      codificadores PNG, ICO, PDF, EPS, TIFF
  levels/           un módulo por nivel
  build.py          orquestador
  verify_formats.py verificación independiente de binarios
  docs/
    PRODUCTION.md   este documento
    COVERAGE.md     qué está hecho y qué NO
  dist/             GENERADO. Desechable. Nunca se edita.
```

**`dist/` no es fuente.** Bórralo cuando quieras: el build es determinista byte
a byte y lo reconstruye idéntico.

## Convención de nombres

```
<plataforma>/<propósito>-<tamaño>.<ext>
```

Ejemplos: `favicon/favicon-32.png`, `android/pwa-512-maskable.svg`,
`social/open-graph-1200x630.png`, `apple/startup-1170x2532.svg`.

Los tamaños van siempre en píxeles. Los lienzos rectangulares usan `AxB`. El
sufijo describe la variante, nunca la fecha ni la versión: la versión vive en el
CDS.

## Reglas de exportación

1. Todo activo sale de la geometría canónica. Ninguno se deriva de otro activo.
2. Ningún SVG se edita a mano. Se regenera.
3. Nada de timestamps, IDs aleatorios ni fechas de creación en ningún formato.
   Rompen el determinismo, y el determinismo es lo que hace útiles los hashes.
4. `gzip` se comprime con `mtime=0` por la misma razón.
5. Las variantes maskable de Android escalan al 40 % del lienzo, no al 56 %,
   para respetar la zona segura del 80 %.
6. El icono monochrome de Android es una silueta plana: el sistema lo tiñe.

## Integración en el sitio

`dist/head-snippet.html` contiene las declaraciones listas para pegar. Se
genera; no se escribe a mano.

Sirve `dist/` en la raíz del dominio, o ajusta las rutas del snippet.

## Cacheado

Los activos son inmutables mientras el `release_digest` no cambie. Recomendado:

```
Cache-Control: public, max-age=31536000, immutable
```

para todo salvo `site.webmanifest` y `browserconfig.xml`, que deberían llevar un
max-age corto. El `release_digest` de `RELEASE.json` sirve como valor de ETag
estable para el conjunto.

## Paso externo: WebP y AVIF

Único punto del sistema donde se admite una herramienta externa.

```bash
cwebp   -lossless dist/social/open-graph-1200x630.png -o open-graph.webp
avifenc --lossless dist/social/open-graph-1200x630.png open-graph.avif
```

No viola la regla de no derivar un activo de otro: es la misma imagen en otro
envoltorio, y la geometría sigue viniendo del CDS. Lo prohibido es redibujar o
re-vectorizar.

## Verificación continua

Cada build debe confirmar:

| Comprobación | Dónde |
|---|---|
| Sin deriva geométrica | L1 gate + L2 C1 |
| Sin cambios de coordenadas | L2 G1–G5 |
| Sin regresión de renderizado | L2 P1–P3 sobre 17 tamaños |
| Sin corrupción de metadatos | L5 Q1–Q3 |
| Sin diferencias de normalización SVG | L5 Q1 |
| Sin discrepancias de hash | `release_digest` |

Un digest de release distinto sin un cambio de CDS deliberado significa que algo
se rompió. Compáralo antes de publicar.

## Modificar el sistema

Cambiar el **CDS** exige una Design Decision formal (ver `CDS.md` §14). Cambiar
un **generador** no toca la identidad, pero cambia el `release_digest`: espera
que cambie y verifica que la geometría no lo hizo.

Ampliar plataformas se hace añadiendo entradas a `SOCIAL`, `SEARCH` o
`FAVICON_SIZES` en `levels/l4_targets.py`. No se añade dibujando nada.

## Antes de publicar, lee esto

`COVERAGE.md` lista lo que este sistema **no** hace: no hay validación en
navegadores reales, no hay WebP ni AVIF, y —lo más importante— **no se ha medido
la tipografía vecina real**, de la que depende el grosor de asta congelado en
DD-009.
