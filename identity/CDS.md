# Canonical Design Specification

**Proyecto:** arjuanfelipe
**Glifo canónico:** `B-PRIME-COMPENSATED` — *B′ · COMPENSATED*
**CDS versión:** 1.0.0
**Estado:** FROZEN
**Fecha de congelación:** 2026-07-30

---

## 0. Cómo leer este documento

Este documento y `cds.json` son la especificación. Los SVG, PNG e iconos del
directorio `build/` son artefactos compilados: se regeneran, nunca se editan.

La dirección de dependencia es inmutable:

```
cds.json  →  geometry.py  →  master.svg  →  activos derivados  →  producción
```

Tres niveles de autoridad, y conviene no confundirlos:

| Nivel | Qué significa | Dónde vive |
|---|---|---|
| **NORMATIVO LITERAL** | Un número escrito. Manda sobre cualquier método que pretenda producirlo. | `parameters`, `control_points`, `path.d` |
| **DERIVADO** | Se calcula en forma cerrada desde los literales. Reproducible exactamente. | `derived`, algoritmo §6 |
| **PROVISIONAL** | Declarado pero no congelado. Pendiente de medida externa. | `metrics` |

Un tercero que solo tenga `cds.json` y `geometry.py` reconstruye el glifo con
fidelidad exacta. `validate.py` lo comprueba en cada build.

---

## 1. Identidad

| Campo | Valor |
|---|---|
| Glifo canónico | `B-PRIME-COMPENSATED` |
| Wordmark | `Now I understand.` |
| Función del glifo | La letra **I** de la frase, y nada más |
| Estado | FROZEN v1.0.0 |
| Supersede a | — (congelación inicial) |
| SHA-256 del path | `cf6b9fe5350776e6514853257925c045b339370c3485d471dca5acaa314d3ad3` |

El glifo no es un logotipo ni un monograma. Es una letra dentro de una frase.
Toda la identidad emerge de ella.

---

## 2. Sistema de coordenadas

| Campo | Valor |
|---|---|
| Unidad | unidad de diseño (du) |
| Unidades por cap height | 1000 |
| Eje X | positivo hacia la derecha |
| Eje Y | **positivo hacia abajo** |
| Origen | esquina superior izquierda de la caja del glifo |
| Línea base | y = 1000 |
| Ascendente | y = 0 |
| Descendente | y = 1000 (el glifo no desciende) |

El eje Y crece hacia abajo para coincidir con el espacio de usuario de SVG.
No se aplica ninguna inversión en la generación. Esto elimina una clase entera
de errores de signo en el pipeline.

---

## 3. Parámetros normativos

Cinco números. Todo lo demás se deriva de ellos.

| Parámetro | Valor | Unidad |
|---|---|---|
| `cap_height` | 1000 | du |
| `stroke_width` | **77.31** | du |
| `overhang` | 36.0 | du |
| `elevation` | 30.0 | du |
| `handle_horizontal` | 0.40 | fracción de `semi_extent` |
| `handle_vertical` | 0.10 | fracción de `elevation` |

> **Aviso sobre `stroke_width`.** Es un literal normativo, **no un valor
> derivado**. Procede de una compensación óptica cuyo método **no converge**:
> re-resolverlo a 100, 160, 240, 320 y 400 px da 77.78, 77.31, 77.72, 77.38 y
> 78.25 — una dispersión de 0.94 du. La masa rasterizada es escalonada, así que
> la bisección converge a un punto arbitrario dentro de un escalón.
> **El número manda; el método es historia.** Ver DD-009.

---

## 4. Valores derivados

Forma cerrada, sin iteración.

```
half_stroke = stroke_width / 2                = 38.655
semi_extent = overhang + half_stroke          = 74.655
axis_x      = semi_extent                     = 74.655
y_top       = half_stroke                     = 38.655
y_bottom    = cap_height - half_stroke        = 961.345
total_width = 2 * semi_extent                 = 149.31
```

**Caja envolvente:** `[0, 0, 149.31, 1000]`, trazo incluido.

Los terminales son cortes verticales, así que no añaden extensión horizontal;
definen exactamente los bordes superior e inferior en `y = 0` y `y = 1000`.

---

## 5. Puntos de control

Normativos. Un generador los emite; no los aproxima.

| Punto | x | y | Función |
|---|---|---|---|
| `P0` | 149.310 | 38.655 | terminal superior |
| `C1` | 119.448 | 38.655 | handle horizontal, tangente horizontal en `P0` |
| `C2` | 74.655 | 41.655 | handle vertical, tangente vertical en `P3` |
| `P3` | 74.655 | 68.655 | encuentro con el asta |
| `L1` | 74.655 | 931.345 | `P3` rotado 180° |
| `Q1` | 74.655 | 958.345 | `C2` rotado 180° |
| `Q2` | 29.862 | 961.345 | `C1` rotado 180° |
| `P6` | 0.000 | 961.345 | terminal inferior |

**Path canónico:**

```
M149.31 38.655 C119.448 38.655 74.655 41.655 74.655 68.655
L74.655 931.345 C74.655 958.345 29.862 961.345 0 961.345
```

Se renderiza siempre como **trazo abierto**, nunca como contorno relleno:

```
fill="none"  stroke-width="77.31"  stroke-linecap="butt"  stroke-linejoin="miter"
```

---

## 5.1 Segmentos

Tres. Ni uno más.

| ID | Tipo | De → a | Controles | Longitud de arco | Giro | Inflexiones |
|---|---|---|---|---|---|---|
| `S1` | Bézier cúbica | `P0 → P3` | `C1`, `C2` | 88.136878 du | 90° | 0 |
| `S2` | recta | `P3 → L1` | — | 862.690000 du | 0° | 0 |
| `S3` | Bézier cúbica | `L1 → P6` | `Q1`, `Q2` | 88.136878 du | 90° | 0 |

**Longitud total de la centerline:** 1038.963756 du

`S3` no se autora: es `S1` rotado 180°. Las dos longitudes difieren en
**5.40 × 10⁻¹³ du** — la simetría de DD-001 se sostiene hasta la precisión de
coma flotante, no solo en los puntos de control.

## 5.2 Tangentes

| Punto | Segmento | t | Vector unitario | Ángulo |
|---|---|---|---|---|
| `P0` | S1 | 0.0 | (−1, 0) | 180.0° |
| `P3` | S1 | 1.0 | (0, +1) | 90.0° |
| `P3→L1` | S2 | — | (0, +1) | 90.0° |
| `L1` | S3 | 0.0 | (0, +1) | 90.0° |
| `P6` | S3 | 1.0 | (−1, 0) | 180.0° |

Error máximo medido frente a estos valores: **0.00e+00**. Son exactos, no
aproximados.

La tangente en los terminales es exactamente horizontal, y de ahí se sigue que
el corte del terminal sea exactamente vertical (DD-003). No es una elección de
estilo: es una consecuencia.

## 5.3 Curvatura

| Posición | κ | κ × grosor | Radio |
|---|---|---|---|
| `P0` (terminal) | 0.0022428086 | 0.173392 | 445.87 du |
| `P3` (unión con asta) | 0.0409629630 | 3.166847 | 24.41 du |
| máximo de S1 (t = 0.8925) | 0.0513619052 | 3.970789 | **19.47 du** |
| `S2` (recta) | 0 | 0 | ∞ |

## 5.4 Continuidad

| Unión | G0 | G1 | G2 |
|---|---|---|---|
| `P3` (S1↔S2) | exacta | **EXACTA** — ambas tangentes (0,1). Error angular cero. | **DISCONTINUA** — salto de 0.0409629630 a 0 |
| `L1` (S2↔S3) | exacta | **EXACTA** | **DISCONTINUA** — misma magnitud |

La discontinuidad G2 está **aceptada**, no pasada por alto. Conseguir G2 exigiría
una curva de transición o un handle mucho más largo, y ambas cosas suben el pico
de curvatura o introducen una decisión que no se deriva de nada. Ver DD-005.

## 5.5 Terminales

| ID | En | Estilo | Corte | Desde | Hasta |
|---|---|---|---|---|---|
| `T-UPPER` | `P0` | butt | vertical, normal a la tangente | (149.31, 0) | (149.31, 77.31) |
| `T-LOWER` | `P6` | butt | vertical, normal a la tangente | (0, 922.69) | (0, 1000) |

Definen exactamente los bordes superior e inferior de la caja envolvente.
`T-LOWER` se deriva de `T-UPPER` por DD-001.

## 5.6 Nota sobre el contorno

El contorno visible es el offset de la centerline a medio grosor. Como el radio
mínimo de curvatura (**19.47 du**) es menor que medio grosor (**38.655 du**), el
offset **interior se autointerseca** y el interior de cada codo se resuelve como
un vértice, no como un arco.

El offset **exterior nunca se autointerseca**: el giro es de exactamente 90° y
monótono (DD-004). Se midieron los anchos de relleno fila a fila y el trazo no se
estrangula en ningún punto. Ver DEF-001 y el test T13.

Esto no es un defecto oculto: es el motivo por el que la unión interior del
remate se ve angulosa, exactamente como en cualquier tipografía con remates.

---

## 6. Algoritmo de construcción

```
half_stroke = stroke_width / 2
semi_extent = overhang + half_stroke
axis_x      = semi_extent
y_top       = half_stroke
y_bottom    = cap_height - half_stroke

rotate180(x, y) = (2*axis_x - x, cap_height - y)

P0 = (axis_x + semi_extent,                        y_top)
C1 = (axis_x + semi_extent*(1 - handle_horizontal), y_top)
C2 = (axis_x,                y_top + elevation*handle_vertical)
P3 = (axis_x,                y_top + elevation)
L1 = rotate180(P3)
Q1 = rotate180(C2)
Q2 = rotate180(C1)
P6 = rotate180(P0)
```

La mitad inferior **nunca se autora**. Se deriva. Es lo que hace exacta la
simetría de DD-001, no aproximada.

---

## 7. Matemáticas

### 7.1 Curvatura de la transición

Para una Bézier cúbica, la curvatura en los extremos:

```
κ(0) = (2/3) · d(C2, recta P0–C1) / |C1 − P0|²
κ(1) = (2/3) · d(C1, recta C2–P3) / |P3 − C2|²
```

Con los valores canónicos: `κmax · stroke_width = 3.971`.

### 7.2 La singularidad que se descartó

Con `handle_horizontal = 1` y `handle_vertical = 0`, la curva adopta forma
cerrada —trasladando el origen al eje, `x = E(1−t)³`, `y = A·t³`— y **ambas
curvaturas extremas se anulan**:

```
κ(t) = (2/3)·E·A·t(1−t) / (E²(1−t)⁴ + A²t⁴)^1.5
```

Es el único punto del plano de handles donde eso ocurre. **Se descartó igualmente.**
Anular la flexión en los bordes la concentra toda en el centro, y produce el
pico de curvatura más alto de la familia: para `E = A`, `κmax = 3.771/E`.
Ver DD-005.

### 7.3 Las dos magnitudes de tinta

No confundirlas — miden cosas distintas:

| Magnitud | Fórmula | Valor | Límite | Contra qué |
|---|---|---|---|---|
| Exceso de longitud | `2·overhang / cap_height` | **7.20 %** | ≤ 10 % (DD-007) | un asta recta del mismo grosor |
| Residuo de masa | integración de área | **−1.35 %** | ±1.5 % (DD-009) | la I de la fuente vecina (85 du) |

La primera acota el gesto. La segunda comprueba que la compensación de asta
hizo su trabajo.

### 7.4 Por qué la compensación no tiene forma cerrada

La masa ideal de un trazo de grosor constante sería `w × L(centerline)`. No lo
es: en el codo el trazo se pisa a sí mismo. Medido a 400 px, la discrepancia
entre el modelo ideal y el área real es de **+3.6 % a +4.4 %** según el grosor.
Depende de cuánta tinta se solapa, que solo se obtiene integrando el área. De
ahí que la compensación se resolviera numéricamente, y de ahí que no converja.

---

## 8. Renderizado

| Regla | Valor |
|---|---|
| Tamaño mínimo legible | 16 px de cap height |
| El gesto se resuelve por encima de | 96 px |
| El gesto es sub-píxel por debajo de | 62 px |
| Antialiasing | **obligatorio** |
| Ajuste a píxel | fijar los bordes del asta a píxeles enteros por debajo de 48 px; el codo cae donde caiga |
| Variante de tamaño pequeño | por debajo de 12 px, sustituir por un asta recta de grosor `stroke_width` |

**Por qué el codo no se ajusta a píxel.** A tamaño pequeño es sub-píxel por
diseño: es exactamente lo que lo mantiene callado al leer. Forzarlo a rejilla lo
haría visible y destruiría la propiedad que justifica DD-007.

**Por qué hay variante pequeña.** Por debajo de 12 px el codo aporta menos de un
píxel de cobertura pero sigue costando tinta, lo que desplaza el color de la
letra sin producir gesto visible. Se paga el precio sin recibir nada.

**Antialiasing.** El glifo no tiene más bordes ortogonales que los caps y los
lados del asta. Desactivar el suavizado destruye el codo por completo.

---

## 9. Defectos conocidos

### DEF-001 — Punto denso en la unión

| Campo | Valor |
|---|---|
| Medición | **+8.00 %** de densidad local en el codo frente al asta |
| Método | integración gaussiana a σ = 0.5 × grosor |
| Control | asta recta sin codo: **+0.00 %** en todos los radios |
| Dependencia de escala | **ninguna** — A/B/C dan +7.53 / +8.00 / +7.41 % |
| Estado | **ACEPTADO, SIN CORREGIR** |

La corrección estándar es adelgazar la unión, lo que rompería DD-002. El defecto
se embarca. Queda documentado para que nunca se vuelva a descubrir como si fuera
un bug.

Que sea independiente del tamaño del gesto significa que **moverse dentro de la
región factible no lo corrige**: pertenece a la familia de curvas, no a esta
elección de parámetros.

---

## 10. Métricas de composición — PROVISIONAL

> **No congelado.** Estos valores dependen de la tipografía vecina y **no se han
> medido contra una fuente real**. No los trates como normativos.

| Campo | Valor provisional |
|---|---|
| Sidebearing izquierdo | 125.3 du |
| Sidebearing derecho | 125.3 du |
| Ancho de avance | 399.91 du |

**Bloqueado por:** medir la cap height y el grosor de asta de la fuente que el
sistema sirve realmente, en cada plataforma de destino. El sitio usa el stack del
sistema, así que varían entre Windows, macOS, iOS y Android.

Hasta que se midan, cualquier composición que use estos números es una
estimación.

---

## 11. Ingeniería

### 11.1 Archivos

| Archivo | Papel |
|---|---|
| `cds.json` | fuente de verdad, legible por máquina |
| `CDS.md` | este documento, especificación normativa |
| `geometry.py` | motor: construcción, Bézier, rasterizado, PNG |
| `generate.py` | genera todos los activos desde el CDS |
| `validate.py` | suite de regresión, 24 comprobaciones |
| `third_party.py` | prueba de completitud: reconstruye usando **solo** `cds.json` |
| `build/` | artefactos compilados, **regenerables** |

Solo dependen de la biblioteca estándar de Python. Sin paquetes externos.

### 11.0 Prueba de completitud

El CDS exige que un tercero sin acceso a ninguna conversación previa pueda
reconstruir el glifo. Eso no se afirma: se ejecuta.

`third_party.py` **no importa `geometry.py`**. Re-implementa la construcción a
partir del algoritmo escrito en la especificación y compara contra los literales.

```
python third_party.py   →  RECONSTRUCTION EXACT  (exit 0)
```

| Comprobación | Resultado |
|---|---|
| 8 puntos de control | error máx. 1.42e−14 du |
| 6 valores derivados | error 0.00e+00 |
| Cadena del path | idéntica |
| SHA-256 | idéntico |
| Simetría rotacional | 0.00e+00 du |
| Caja envolvente | 0.00e+00 du |

Si este script falla, el CDS está incompleto por su propia definición y no debe
publicarse.

### 11.2 Puerta de generación

`generate.py` aborta si la reconstrucción desde los parámetros no coincide con
los puntos de control literales, o si el path generado difiere del path del CDS.
Es imposible emitir activos desde un CDS incoherente.

### 11.3 Suite de regresión

```
python validate.py     →  24 passed, 0 failed  (exit 0)
```

| Test | Comprueba |
|---|---|
| T01 | la reconstrucción coincide con los literales (desviación máx. 1.42e−14 du) |
| T02 | el path generado es idéntico al del CDS |
| T03 | simetría rotacional **exacta**: error 0.00e+00 |
| T04 | tangente horizontal en el terminal: dy = 0 |
| T05 | continuidad G1 con el asta: dx = 0 |
| T06 | transición monótona, sin inflexión |
| T07 | caja envolvente 149.310 × 1000.000 |
| T08 | el tramo recto sobrevive (86.3 % de la cap height) |
| T09 | exceso de longitud 7.20 % dentro del límite del 10 % |
| T10 | el gesto es sub-píxel a 16 px (0.480 px) |
| T11 | el gesto se resuelve a 96 px (2.88 / 3.46 px) |
| T12 | voladizo > elevación (36 > 30) |
| T13 | el trazo no se estrangula (medido, no supuesto) |
| T14 | la unión interior es angulosa, como se documenta |
| T15 | DEF-001 está declarado |
| T16 | DD-009 lleva su aviso de no convergencia |
| T17 | las métricas están marcadas PROVISIONAL |
| T18 | el sha256 declarado coincide con el path construido |
| T19 | las longitudes de segmento declaradas son correctas |
| T20 | los arcos superior e inferior miden lo mismo (5.40e−13 du) |
| T21 | las tangentes declaradas son correctas (error 0.00e+00) |
| T22 | el salto G2 declarado coincide con la medición |
| T23 | la geometría del corte terminal coincide |
| T24 | el offset interior se autointerseca, como se documenta |

T15, T16 y T17 no comprueban geometría: comprueban que **la especificación
sigue diciendo la verdad sobre sí misma**. Si alguien borra el aviso de no
convergencia de DD-009, el build falla.

T18 a T24 cumplen la misma función para el bloque `curves`: cada número
declarado allí se vuelve a medir en cada build. Una especificación que declara
valores sin comprobarlos no vale más que un comentario.

### 11.4 Precisión

| Magnitud | Requisito |
|---|---|
| Puntos de control | 0.001 du |
| Grosor de trazo | 0.01 du |
| Error de simetría rotacional | **0.0 du — exacto** |
| Residuo de masa | ±1.5 % |

### 11.5 Activos generados

20 archivos: `master.svg`, `glyph-inline.svg`, `glyph-small.svg`,
`favicon-{16,32,48}.svg`, `apple-touch-icon.svg`, `pwa-{192,512}.svg` y sus
variantes maskable, `og-image.svg`, `print-40mm.svg`, `favicon-datauri.txt`,
`manifest.webmanifest`, `BUILD.json`, e `icon-{16,32,48,180}.png` rasterizados
desde la misma geometría.

Las variantes maskable escalan al 40 % del lienzo, no al 56 %, para respetar la
zona segura del 80 % de Android.

---

## 12. Decisiones congeladas

Diez decisiones. Ninguna puede desaparecer; solo puede ser superada por otra
posterior con justificación técnica completa.

| ID | Título | Confianza |
|---|---|---|
| DD-001 | Simetría rotacional de 180° | ALTA |
| DD-002 | Grosor de trazo constante | ALTA |
| DD-003 | Terminaciones a escuadra | ALTA |
| DD-004 | Transición monótona de 90° | ALTA |
| DD-005 | Valores de los handles | MEDIA |
| DD-006 | Rechazo de la geometría de la ronda 01 | ALTA |
| DD-007 | Región factible del gesto | MEDIA |
| DD-008 | Selección del candidato B | **BAJA** |
| DD-009 | Asta compensada; herencia abandonada | **BAJA** |
| DD-010 | Punto denso aceptado sin corregir | ALTA |

El detalle completo de cada una —regla previa, regla nueva, evidencia,
justificación, implicaciones de ingeniería, impacto aguas abajo— está en
`cds.json`, campo `decisions`.

### Las dos decisiones débiles

Conviene que estén señaladas, no enterradas:

**DD-008 (selección del candidato B) — confianza BAJA.** Es la decisión más
débil del CDS. Se tomó por selección, no por evidencia: ninguna restricción
derivable separaba los 435 puntos de la región factible. La pregunta perceptual
que habría discriminado entre A, B y C **nunca se respondió**.

**DD-009 (asta compensada) — confianza BAJA.** Supera una regla previamente
congelada: el asta ya no hereda el grosor de la tipografía vecina, sino que es un
9.0 % más fina. Se ha cambiado una delación (peso) por otra (grosor de asta). Y
su derivación no converge, por lo que el valor es normativo por congelación.

---

## 13. Historial de versiones

| Versión | Fecha | Resumen |
|---|---|---|
| 1.0.0 | 2026-07-30 | Congelación inicial. Glifo canónico B′ · COMPENSATED. DD-001 a DD-010. |

---

## 14. Cómo superar una decisión congelada

1. Nueva entrada en `decisions` con `id` siguiente, fecha, regla previa y nueva.
2. Evidencia objetiva. No preferencia.
3. Implicaciones de ingeniería e impacto aguas abajo, explícitos.
4. La decisión anterior pasa a `status: "SUPERSEDED_BY: DD-0xx"`. **No se borra.**
5. Subir `cds_version` y añadir entrada al historial.
6. `validate.py` debe pasar antes de regenerar activos.

Ninguna regla congelada desaparece jamás. La trazabilidad histórica no se pierde.
