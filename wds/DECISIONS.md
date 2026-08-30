# WDS — Decisiones de diseño

Cada decisión en el formato requerido: propósito, razón, dependencias, tokens
consumidos, accesibilidad, rendimiento, comportamiento responsive y
extensibilidad.

El WDS consume el CDS 1.0.0 y el IPS. No los modifica. `build_wds.py` abre
`cds.json` en solo lectura y verifica su digest: una identidad que hubiera
derivado detiene la compilación.

---

## WDS-001 · Los colores semánticos se derivan por rotación de matiz

**Propósito.** Obtener `success`, `warning`, `danger` e `info` sin introducir
colores ajenos a la identidad.

**Razón.** El encargo pide colores semánticos y a la vez prohíbe inventar
colores fuera de la paleta canónica, que no contiene ni verde ni rojo. La
salida es derivarlos: cada semántico es el accent canónico rotado en matiz
dentro de OKLCH, con luminancia y croma fijos. Son el mismo color en otro
ángulo, no colores nuevos. Como OKLCH es perceptualmente uniforme y la
luminancia no se mueve, **el contraste queda garantizado por construcción**.

| | rotación | hex | H |
|---|---|---|---|
| primary | 0° | `#ea6a1e` | 45,7 |
| warning | +49,3° | `#b09300` | 94,9 |
| success | +104,3° | `#1ab256` | 150,1 |
| info | +194,3° | `#009fe9` | 240,0 |
| danger | +334,3° | `#ee5f66` | 20,3 |

**Dependencias.** `canonical_palette.accent` del CDS.
**Tokens.** `--wds-primary|success|warning|danger|info` y sus `-surface`.
**Accesibilidad.** Los cinco superan 4,5:1 sobre el fondo en ambos temas
(5,69–6,64 en oscuro). **Limitación declarada:** `danger` queda a solo **25,4°**
de `primary`. Con un accent naranja no puede separarse más sin salir de la
familia; nunca deben aparecer adyacentes sin etiqueta de texto, y el color no
puede ser el único portador del significado.
**Rendimiento.** Ninguno: se resuelve en build, el CSS solo lleva hex.
**Responsive.** Sin efecto.
**Extensibilidad.** Un semántico nuevo es una línea en `tokens.json`.

---

## WDS-002 · Los tokens con contrato se resuelven, no se eligen

**Propósito.** Que ningún valor de accesibilidad dependa del ojo de quien
escribió la hoja de estilos.

**Razón.** `border-strong` es la única señal visual de algunos controles, así
que WCAG 1.4.11 le exige 3:1. Fijar una luminancia a mano y esperar que cumpla
falló: daba 2,50 y 2,37. El sistema ahora **resuelve** el token — mantiene
matiz y croma, y mueve la luminancia hasta alcanzar el ratio.

Resultado: `#5d6269` a 3,005:1 en oscuro (21 iteraciones), `#8c9199` a 3,03:1
en claro (32 iteraciones).

**Dependencias.** Fondo del tema.
**Tokens.** `--wds-border-strong`.
**Accesibilidad.** Es el propósito entero.
**Rendimiento.** Build-time.
**Responsive.** Sin efecto.
**Extensibilidad.** Cualquier token puede pasar a resolverse por contrato
añadiéndolo al paso de resolución.

---

## WDS-003 · Cero JavaScript, y lo que eso cuesta

**Propósito.** Respetar la decisión congelada §14 sin fingir cobertura.

**Razón.** La mayoría de lo que se cree que necesita JS no lo necesita:
acordeones y navegación móvil son `<details>`, los diálogos son `<dialog>`, los
tooltips son `:focus-within`. Todos son accesibles por teclado sin una línea de
script.

**Lo que sí necesitaría JS y no se ha falseado:**

| Componente | Por qué |
|---|---|
| Búsqueda | requiere índice y filtrado en cliente o servidor |
| Filtrado de listas | mismo motivo |
| Tooltips en espacio estrecho | requiere motor de posicionamiento |
| Selector de tema manual | el automático funciona; el conmutador necesita persistencia |

**Dependencias.** Elementos nativos del navegador.
**Tokens.** Todos los de motion y z-index.
**Accesibilidad.** Mejor que la media: los elementos nativos traen semántica,
foco y teclado resueltos por la plataforma.
**Rendimiento.** 0 KB de JS. CSS total **27,9 KB, 5,9 KB con gzip**.
**Responsive.** La navegación colapsa a `<details>` bajo 720 px.
**Extensibilidad.** Introducir JS exige una decisión formal que supere §14.

---

## WDS-004 · La profundidad es luminancia, no sombra

**Propósito.** Que la jerarquía de superficies funcione en oscuro.

**Razón.** Sobre un fondo oscuro una sombra es casi invisible: proyectar negro
sobre negro no separa nada. La pila de superficies se construye subiendo
luminancia en OKLCH conservando matiz y croma del fondo canónico, así que cada
superficie es *el mismo color a otra profundidad*. La sombra queda como refuerzo
secundario, no como mecanismo.

**Dependencias.** `canonical_palette.background`.
**Tokens.** `--wds-bg`, `--wds-surface`, `--wds-surface-elevated`,
`--wds-surface-interactive`.
**Accesibilidad.** Texto principal ≥ 12,71:1 sobre cualquier superficie.
Verificado que la pila es monótona en luminancia en ambos temas (test T14).
**Rendimiento.** Sin sombras que pintar en la mayoría de casos; en OLED se
desactivan por completo.
**Responsive.** Sin efecto.
**Extensibilidad.** Un nivel más es una entrada en `surface_lightness`.

---

## WDS-005 · Escala tipográfica fluida que no encoge el cuerpo de texto

**Propósito.** Jerarquía que sobreviva de 360 a 1280 px.

**Razón.** Escala modular de 1,25 anclada en 16 px. La compresión en móvil es
proporcional al paso: el cuerpo **no encoge nunca** (16 px siempre) y los
títulos comprimen más cuanto más grandes. Un `display` que baja de 61 a 37,8 px
sigue mandando; un cuerpo de 14 px sería más difícil de leer sin ganar nada.

**Dependencias.** Ninguna externa.
**Tokens.** `--wds-text-*` (9 pasos, todos `clamp()`).
**Accesibilidad.** Cuerpo fijo en 16 px; medida limitada a 68ch;
`text-wrap: balance` en títulos y `pretty` en párrafos.
**Rendimiento.** `clamp()` es nativo, sin media queries por paso.
**Responsive.** Es el mecanismo.
**Extensibilidad.** Un paso nuevo es una entrada en `type_scale.steps`.

---

## WDS-006 · Motion se apaga en el token, no en el componente

**Propósito.** Que `prefers-reduced-motion` no dependa de que cada componente
se acuerde de respetarlo.

**Razón.** La forma habitual —un override por componente— falla en cuanto
alguien añade el componente número 36 y olvida la regla. Aquí las duraciones
colapsan a 1 ms **en `:root`**, así que todo lo que use los tokens obedece sin
escribir una sola excepción.

**Dependencias.** Ninguna.
**Tokens.** `--wds-duration-*`, `--wds-ease-*`.
**Accesibilidad.** Es el propósito. La única animación real (skeleton) además
se desactiva explícitamente.
**Rendimiento.** Solo se anima `opacity`, `color`, `background-color`,
`border-color` y `transform`: nada que fuerce layout.
**Responsive.** Sin efecto.
**Extensibilidad.** Un componente nuevo hereda el comportamiento gratis.

---

## WDS-007 · El glifo se consume, nunca se declara

**Propósito.** Mantener inmutable la dirección de dependencia CDS → IPS → WDS.

**Razón.** El CSS del WDS **no contiene geometría**: solo dimensiona el glifo
(`height: 0.70em`, el cap height del texto vecino) y lo sienta en la línea base
(`vertical-align: 0`). El `path` vive en el CDS. Verificado por el test T12.

**Dependencias.** `cds.json`, verificado por digest en cada build.
**Tokens.** `--wds-fg` vía `currentColor`.
**Accesibilidad.** `aria-hidden` cuando el texto vecino ya lee la letra.
**Rendimiento.** SVG inline, sin petición extra.
**Responsive.** Escala con el tipo por estar en `em`.
**Extensibilidad.** Un cambio en el CDS se propaga solo.

---

## WDS-008 · La integridad referencial se comprueba en cada build

**Propósito.** Cazar el fallo más peligroso de un sistema de tokens.

**Razón.** Una `var(--wds-algo)` inexistente **no lanza error**: CSS cae al
valor heredado y el layout se rompe en silencio. En este mismo build el
validador encontró `--wds-space-5` y `--wds-space-14` referenciados pero no
definidos. Sin el test habrían llegado a producción sin avisar.

**Dependencias.** CSS emitido.
**Tokens.** Todos: 88 referencias contra 123 definiciones.
**Accesibilidad.** Indirecta: un token de foco roto elimina el foco visible.
**Rendimiento.** Build-time.
**Responsive.** Sin efecto.
**Extensibilidad.** El test no necesita mantenimiento: lee el CSS real.

> **Nota sobre la cobertura de escala (62%).** Una escala es una paleta cerrada
> de valores permitidos; existe para que los componentes futuros elijan de ella
> en lugar de inventar números. Los peldaños sin usar son deliberados, no deuda.
> Solo se exige que estén referenciados los tokens **semánticos**, que apuntan a
> algo concreto.

---

## WDS-009 · La documentación es auto-contenida, no enlazada

**Propósito.** Que la página sobreviva a que la muevan de carpeta.

**Razón.** La página se emitía con `<link rel="stylesheet" href="../css/wds.css">`.
Ese `href` solo resuelve desde el directorio para el que se escribió: al
copiarla a `paleta_canonica/` apuntó a una ruta inexistente y **perdió todos
los estilos en silencio** —CSS no lanza error por una hoja que no carga. El
build ahora **incrusta** `wds.css` en la página. Sigue habiendo una sola
fuente: se inyecta en build desde el mismo archivo generado, y el test T20
comprueba que lo incrustado es `css/wds.css` literal, no una copia.

Un único render se escribe en los dos destinos (`wds/docs/index.html` y
`paleta_canonica/paleta_canonica.html`), los dos con hash en el manifiesto y
verificados byte a byte por T18. Una copia hecha a mano ya se quedó obsoleta
una vez; no se repite el mecanismo que falló.

**Dependencias.** `css/wds.css` del mismo build.
**Tokens.** Todos, incrustados.
**Accesibilidad.** Directa: una página sin estilos pierde foco visible,
objetivos táctiles y contraste a la vez.
**Rendimiento.** 62 KB en un archivo, sin segunda petición. Para una página de
documentación abierta desde disco, es la opción correcta; **no** es el patrón
para páginas de producción, que deben cachear la hoja aparte.
**Responsive.** Sin efecto.
**Extensibilidad.** Un destino nuevo es una línea en `DOC_TARGETS`.

---

## WDS-010 · Lo que apareció al abrirla en un navegador

**Propósito.** Cerrar el hueco declarado en las fases anteriores.

**Razón.** Hasta ahora la validación era estructural. Al renderizar la página
en Chromium aparecieron **tres defectos que ningún test de cálculo podía ver**,
y ninguno era de color ni de contraste:

| # | Defecto | Origen | Corrección |
|---|---|---|---|
| 1 | `<dialog open>` flotaba sobre la sección siguiente y la tapaba | `position: absolute` del UA stylesheet | la demo vuelve al flujo; el componente conserva lo que `showModal()` necesita |
| 2 | 322 px de desbordamiento horizontal a 375 px | rejillas de la doc de 34,5 rem y barras de 512 px | los swatches reflowean; la escala de espaciado hace scroll en su propia caja |
| 3 | el menú móvil descuadraba la barra al abrirse | el `<details>` crecía dentro de la fila flex del header | el panel abierto pasa a `position:absolute` bajo la cabecera |

El nº 3 era un defecto **del sistema**, no de la documentación: `.wds-nav-toggle`
estaba roto en su propio breakpoint desde que se escribió.

**Dependencias.** Ninguna nueva.
**Tokens.** Sin cambios.
**Accesibilidad.** Verificado en render real, ya no por construcción: anillo de
foco dibujado en `#ff8444` a 2 px, enlace de salto que aparece al tabular,
tooltip que responde a `:focus-within`, y 44 px de alto en cada enlace del menú
móvil. Los 33 elementos enfocables tienen nombre accesible.
**Rendimiento.** Sin efecto.
**Responsive.** Es el asunto: 320, 375 y desktop sin desbordamiento del body.
**Extensibilidad.** T16 impide que un componente vuelva a quedar sin mostrar,
que es lo que mantenía estos fallos fuera de la vista.

---

## Inventario de páginas soportado

Home, About, Projects, Research, Writing, Experiments, Notes, Uses, Resume,
Contact, 404, Search, Privacy.

Todas se componen con los mismos primitivos: `.wds-container`, `.wds-grid`,
`.wds-stack`, `.wds-section` más los componentes. **Search** es la única que
requeriría JavaScript (ver WDS-003).

---

## Lo que NO he verificado

Igual que en las fases anteriores, esto se declara en vez de darse por hecho:

- **Solo se ha probado en Chromium.** La página se abrió y se recorrió en un
  navegador real (ver WDS-010), pero en uno. **Firefox y Safari siguen sin
  probarse**, y son justo donde `color-mix()`, `text-wrap: pretty` y el
  posicionamiento de `<dialog>` tienen más probabilidad de divergir.
- **No he probado con lector de pantalla.** La semántica es correcta por
  construcción y los 33 elementos enfocables tienen nombre accesible, pero
  nadie lo ha escuchado. Un nombre accesible correcto no garantiza que el
  anuncio sea comprensible.
- **No hay pruebas de regresión visual automatizadas.** La verificación de
  WDS-010 fue manual: cierra el hueco de hoy, no impide el de mañana. Ningún
  test del suite detecta un desbordamiento horizontal —eso requiere un motor de
  render dentro del build, que no existe aquí.
- **No se ha probado en un navegador antiguo real.** `color-mix()` y
  `text-wrap: pretty` degradan con elegancia sobre el papel; no lo he visto.
