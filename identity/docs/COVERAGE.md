# Cobertura del IPS — qué está hecho y qué no

Este documento existe para que nadie confunda una casilla marcada con un
trabajo hecho. Lo que no se pudo producir aparece aquí, no escondido en una
lista de entregables.

**Build de referencia:** 110 activos · release digest
`9f667d190b155bebc0f36ea5bf428f0754e80b16214df6235dedaf14195e5945`

---

## 1. Producido y verificado

| Área | Estado | Verificación ejecutada |
|---|---|---|
| SVG (19 variantes) | ✅ | XML bien formado, viewBox validado |
| PNG (34 archivos) | ✅ | chunks recorridos, CRC verificado, IDAT descomprimido |
| ICO (2 archivos) | ✅ | cada miembro re-parseado como PNG y contrastado con su tamaño declarado |
| PDF vectorial | ✅ | xref re-parseado, cada offset cae sobre su objeto |
| EPS vectorial | ✅ | conforme a DSC, BoundingBox y path presentes |
| TIFF archivo | ✅ | IFD re-parseado, 12 tags en orden ascendente, longitud de strip coherente |
| Sistema de favicons | ✅ | 12 tamaños PNG + ICO multi-resolución + SVG |
| Apple | ✅ | touch icons, mask icon, 7 startup images |
| Android | ✅ | adaptive, legacy, round, monochrome, maskable, Play Store |
| Windows | ✅ | tiles, store icon, ICO de Explorer, browserconfig.xml |
| Social (19 plataformas) | ✅ | SVG siempre; PNG donde la plataforma rechaza SVG |
| Buscadores (7) | ✅ | PNG al tamaño que cada rastreador documenta |
| PWA | ✅ | manifest con maskable y monochrome |
| Determinismo | ✅ | dos builds completos, 111 archivos, 0 diferencias |
| Trazabilidad criptográfica | ✅ | SHA-256 por activo + digest de release |

---

## 2. NO producido, con la razón

### WebP y AVIF — no generados

Exigen implementar un codificador **VP8L** (WebP lossless) o **AV1 intra**
(AVIF). Son miles de líneas de código de compresión de imagen, y una
implementación casera tendría alta probabilidad de producir archivos sutilmente
corruptos que solo fallarían en algunos decodificadores.

**Qué hacer:** generarlos desde los PNG del release con `cwebp` y `avifenc`.
Es el único punto del sistema donde se admite una herramienta externa, y está
justificado. El paso queda documentado en `PRODUCTION.md`.

> Nota: esto **no** viola la regla de no derivar un activo de otro. El PNG y el
> WebP serían la misma imagen en dos envoltorios; la geometría sigue viniendo
> del CDS. Lo que la regla prohíbe es redibujar o re-vectorizar.

### JPEG — no generado, y no debería generarse

Exige un codificador DCT. Además es el formato equivocado: DCT sobre un trazo
duro de dos tonos produce *ringing* visible en los bordes. Para documentación,
usar PNG.

### Validación de renderizado en navegadores — NO EJECUTADA

Pides validar en Chrome, Firefox, Safari, Edge, Opera, Arc, Brave y navegadores
móviles. **No tengo navegadores.** No he abierto ni un solo activo en ningún
motor de renderizado.

Lo que sí se hizo, y no es lo mismo: cada SVG se parsea como XML, se valida su
viewBox, y el glifo se rasteriza con un rasterizador propio en 17 tamaños. Eso
detecta SVG malformado y colapso de trazo. **No detecta** diferencias de
renderizado entre motores, bugs de `stroke-linecap` en Safari, ni cómo trata
cada navegador `currentColor` en un favicon.

**Qué hacer:** abrir `dist/` en cada navegador objetivo. Es trabajo manual y no
lo he sustituido por nada.

### Integración tipográfica — NO MEDIDA

Pides medir la interacción con Inter, Geist, IBM Plex Sans, SF Pro, Segoe UI,
Roboto, Helvetica y Arial. **No tengo esas fuentes** ni forma de medir sus
métricas reales.

Esto es grave, no cosmético: el CDS marca las métricas de composición como
**PROVISIONAL** precisamente porque dependen de esa medida, y DD-009 congeló un
grosor de asta calculado contra una referencia *estimada* de 85 du. Si el stem
real de la fuente vecina no es 85, la compensación entera apunta al valor
equivocado.

**Qué hacer:** medir cap height y grosor de asta de la mayúscula I en cada
fuente objetivo, y comparar con `stroke_width = 77.31`. Es la tarea más
importante que queda pendiente en todo el proyecto.

### Brotli — no medido

No está en la biblioteca estándar de Python. Sí se midió gzip, que es
determinista con `mtime=0`.

### Validación W3C — no ejecutada

Requiere el servicio del W3C. Se usó el parser XML de la biblioteca estándar,
que detecta malformación pero no incumplimientos del esquema SVG.

---

## 3. Producido pero con salvedad

### Validación óptica

Se mide en 17 tamaños: colapso de trazo, ancho mínimo del asta, proporción de
píxeles con antialiasing, y simetría del raster. Todo es **medición**, no
juicio. "Equilibrio visual" y "reconocimiento" aparecen en tu lista y no son
computables: nadie ha mirado estos iconos.

### Simetría del raster

El primer intento midió 1.0000 de asimetría y detuvo el pipeline. El fallo era
del test, no del glifo: en un lienzo de dimensiones enteras el sobrante
fraccionario cae entero a un lado, y rotar 180° mide el encuadre. Con el glifo
centrado a nivel sub-píxel la simetría da **0.0000 exacto**. La función
`coverage_centred` existe solo por esto.

### Precisión decimal a 1 decimal

Desviación máxima de **0.0480 du** contra un presupuesto de 0.05. Pasa, pero
por poco. La variante de producción usa 2 decimales (0.0050 du). Si alguien
baja el presupuesto, la variante Tiny es la primera que cae.

### Contorno relleno

El `outline` se genera por muestreo a 400 puntos con un error de cuerda de
**2.378e-04 du**. No es una conversión analítica de trazo a contorno: es una
poligonal densa. Para uso en pantalla e impresión es indistinguible; para
generar una fuente OpenType conviene una conversión analítica.

---

## 4. Resumen sin adornos

| | |
|---|---|
| Entregado y verificado | formatos vectoriales y raster, todas las plataformas, determinismo, hashes |
| Imposible aquí | WebP, AVIF, JPEG |
| No ejecutado por falta de herramienta | validación en navegadores, W3C, brotli |
| **No ejecutado y bloquea una decisión congelada** | **medición tipográfica real** |

El último punto es el que importa. Todo lo demás son huecos de herramienta; ese
es un hueco de evidencia que afecta a DD-009.
