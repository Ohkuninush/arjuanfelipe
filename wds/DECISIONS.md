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

## Inventario de páginas soportado

Home, About, Projects, Research, Writing, Experiments, Notes, Uses, Resume,
Contact, 404, Search, Privacy.

Todas se componen con los mismos primitivos: `.wds-container`, `.wds-grid`,
`.wds-stack`, `.wds-section` más los componentes. **Search** es la única que
requeriría JavaScript (ver WDS-003).

---

## Lo que NO he verificado

Igual que en las fases anteriores, esto se declara en vez de darse por hecho:

- **No he abierto esta hoja de estilos en ningún navegador.** No tengo Chrome,
  Firefox, Safari ni Edge. La validación es estructural —integridad referencial,
  contraste por cálculo, parseo— no visual.
- **No he probado con lector de pantalla.** La semántica es correcta por
  construcción (elementos nativos, ARIA donde toca), pero nadie lo ha escuchado.
- **No hay pruebas de regresión visual.** Requieren un motor de render.
- **`color-mix()` y `text-wrap: pretty`** son razonablemente recientes; degradan
  con elegancia, pero no lo he comprobado en un navegador antiguo real.
