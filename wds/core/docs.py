# -*- coding: utf-8 -*-
"""
WDS living documentation.

The page is emitted SELF-CONTAINED: wds.css is inlined at build time rather
than linked. A relative <link href="../css/wds.css"> only resolves from the
one directory it was written for -- move the file and the page silently loses
every style. Inlining the same generated CSS keeps a single source of truth
and makes the artefact position-independent.

Every component defined in components.css appears here at least once. That is
not a convention anyone has to remember: validate_wds.py fails the build if a
class exists in the stylesheet and never shows up on this page.
"""

from core.colour import contrast, rgb_to_oklch, hex_to_rgb
from core.css import type_scale


DOC_CSS = """
  .doc { max-width: var(--wds-container); margin-inline: auto; padding: var(--wds-space-12) var(--wds-margin) var(--wds-space-24); }
  .doc section { padding-block: var(--wds-space-14); border-top: 1px solid var(--wds-border-subtle); }
  .doc section:first-of-type { border-top: 0; padding-block: 0; }
  .eyebrow { font-family: var(--wds-font-mono); font-size: var(--wds-text-caption); letter-spacing: var(--wds-tracking-caps); color: var(--wds-accent); margin-bottom: var(--wds-space-4); }
  .sw { display: grid; grid-template-columns: 2.5rem 15rem 6rem 5.5rem 5.5rem auto; gap: var(--wds-space-3); align-items: center; padding: var(--wds-space-2) 0; border-bottom: 1px solid var(--wds-border-subtle); font-family: var(--wds-font-mono); font-size: var(--wds-text-caption); }
  .sw__chip { width: 2.5rem; height: 1.5rem; border-radius: var(--wds-radius-sm); border: 1px solid var(--wds-border); display: block; }
  .sw__hex, .sw__num { color: var(--wds-fg-tertiary); }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  .sp { display: grid; grid-template-columns: 8rem 12rem auto; gap: var(--wds-space-4); align-items: center; padding: var(--wds-space-1) 0; font-family: var(--wds-font-mono); font-size: var(--wds-text-caption); }
  .sp__bar { height: 10px; background: var(--wds-accent); border-radius: 2px; display: block; }
  .demo { display: flex; flex-wrap: wrap; gap: var(--wds-space-4); align-items: center; margin-block: var(--wds-space-5); }
  .grid-demo > div { background: var(--wds-surface); border: 1px solid var(--wds-border-subtle); padding: var(--wds-space-2); text-align: center; font-family: var(--wds-font-mono); font-size: 11px; color: var(--wds-fg-tertiary); border-radius: var(--wds-radius-sm); }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem,1fr)); gap: var(--wds-space-5); }
  .spec { font-family: var(--wds-font-mono); font-size: var(--wds-text-caption); color: var(--wds-fg-quiet); margin-block: var(--wds-space-2) var(--wds-space-4); }
  .doc h3 { margin-top: var(--wds-space-10); }
  .doc h3:first-of-type { margin-top: var(--wds-space-6); }
  /* A non-modal <dialog open> is position:absolute per the UA stylesheet, so
     on this page it floats over the next section. Only the demo is pinned
     back into flow; the component keeps the positioning showModal() needs. */
  .doc .wds-dialog[open] { position: static; margin: var(--wds-space-5) 0; }
  /* Wide content scrolls inside its own box. The page body never does. */
  .scroller { overflow-x: auto; }
  @media (max-width: 719px) {
    /* The swatch table is 34.5rem of fixed columns: it cannot fit a phone.
       It reflows rather than scrolls, because each field is readable alone. */
    .sw { display: flex; flex-wrap: wrap; gap: var(--wds-space-1) var(--wds-space-3); }
    .sw code { flex: 1 1 auto; }
    .sw__chip { flex: 0 0 auto; }
    .sw__hex, .sw__num { text-align: left; }
    /* The spacing bars scroll instead: a truncated bar would be a lie about
       the value it represents. */
    .sp { grid-template-columns: 5rem 8rem auto; }
  }
"""


def _glyph(cds):
    d = cds["path"]["d"]
    vb = f"0 0 {cds['bounding_box']['width']} {cds['bounding_box']['height']}"
    sw = cds["parameters"]["stroke_width"]
    return (f'<svg class="wds-glyph" viewBox="{vb}" aria-hidden="true">'
            f'<path d="{d}" stroke-width="{sw}"/></svg>')


def _swatches(col, theme):
    out = []
    skip = ("selection", "code-bg", "scrollbar-thumb", "scrollbar-track")
    for k, v in col[theme].items():
        if k.endswith("-surface") or k in skip:
            continue
        c = contrast(v, col[theme]["bg"])
        L, C, H = rgb_to_oklch(hex_to_rgb(v))
        out.append(
            f'<div class="sw"><span class="sw__chip" style="background:{v}">'
            f'</span><code>--wds-{k}</code><span class="sw__hex">{v}</span>'
            f'<span class="sw__num">L {L:.3f}</span>'
            f'<span class="sw__num">H {H:5.1f}</span>'
            f'<span class="sw__num">{c:5.2f}:1</span></div>')
    return "".join(out)


def _components(glyph):
    """
    The component gallery. Ordered by how often a page actually reaches for
    them, not by how they sit in the stylesheet.
    """
    return f"""
  <h3>Botones</h3>
  <p class="spec"><code>.wds-btn</code> · <code>--primary</code>
    <code>--secondary</code> <code>--ghost</code> <code>--danger</code>
    <code>--sm</code></p>
  <div class="demo">
    <button class="wds-btn wds-btn--primary">Primario</button>
    <button class="wds-btn wds-btn--secondary">Secundario</button>
    <button class="wds-btn wds-btn--ghost">Fantasma</button>
    <button class="wds-btn wds-btn--danger">Peligro</button>
    <button class="wds-btn wds-btn--secondary" disabled>Desactivado</button>
  </div>
  <div class="demo">
    <button class="wds-btn wds-btn--sm wds-btn--primary">Pequeño</button>
    <button class="wds-btn wds-btn--sm wds-btn--secondary">Pequeño</button>
    <span class="wds-caption">La variante <code>--sm</code> baja a 32&nbsp;px:
      queda por debajo del objetivo táctil, así que solo con ratón.</span>
  </div>

  <h3>Insignias y etiquetas</h3>
  <p class="spec"><code>.wds-badge</code> · <code>.wds-tag</code></p>
  <div class="demo">
    <span class="wds-badge">NEUTRA</span>
    <span class="wds-badge wds-badge--success">SUCCESS</span>
    <span class="wds-badge wds-badge--warning">WARNING</span>
    <span class="wds-badge wds-badge--danger">DANGER</span>
    <span class="wds-badge wds-badge--info">INFO</span>
  </div>
  <div class="demo">
    <span class="wds-tag">geometría</span>
    <span class="wds-tag">OKLCH</span>
    <span class="wds-tag">tipografía</span>
    <span class="wds-tag">determinismo</span>
  </div>

  <h3>Tarjetas</h3>
  <p class="spec"><code>.wds-card</code> · <code>--interactive</code>
    <code>__title</code> <code>__meta</code></p>
  <div class="cards">
    <article class="wds-card wds-card--interactive">
      <p class="wds-card__meta">PROYECTO · 2026</p>
      <h4 class="wds-card__title">Identity Production System</h4>
      <p>110 activos generados desde una especificación de 5 números.</p>
    </article>
    <article class="wds-card wds-card--interactive">
      <p class="wds-card__meta">NOTA</p>
      <h4 class="wds-card__title">Sobre la simetría rotacional</h4>
      <p>Una I normal es simétrica por espejo. Ésta lo es por rotación.</p>
    </article>
    <article class="wds-card">
      <p class="wds-card__meta">ESTÁTICA</p>
      <h4 class="wds-card__title">Sin estado de hover</h4>
      <p>Una tarjeta que no lleva a ningún sitio no debe reaccionar como si
        llevara.</p>
    </article>
  </div>

  <h3>Avisos</h3>
  <p class="spec"><code>.wds-callout</code> · <code>--info</code>
    <code>--success</code> <code>--warning</code> <code>--danger</code></p>
  <div class="wds-stack">
    <div class="wds-callout wds-callout--info"><span class="wds-callout__label">Info</span><div>El sistema es dark-first; el tema claro se deriva del mismo motor.</div></div>
    <div class="wds-callout wds-callout--success"><span class="wds-callout__label">Listo</span><div>Los 32 contratos de contraste se resuelven en el build.</div></div>
    <div class="wds-callout wds-callout--warning"><span class="wds-callout__label">Cuidado</span><div>El grosor del asta está congelado contra una referencia estimada.</div></div>
    <div class="wds-callout wds-callout--danger"><span class="wds-callout__label">Peligro</span><div>Ningún componente introduce JavaScript sin justificarlo.</div></div>
  </div>

  <h3>Acordeón <span class="wds-badge">&lt;details&gt;</span></h3>
  <p class="spec"><code>.wds-accordion</code> · <code>__body</code></p>
  <details class="wds-accordion"><summary>¿Por qué cero JavaScript?</summary>
    <div class="wds-accordion__body">Porque hasta ahora ninguna interacción lo
      ha exigido. Acordeones, navegación móvil y diálogos existen como elementos
      nativos, accesibles por teclado sin una línea de script.</div></details>
  <details class="wds-accordion"><summary>¿Qué necesitaría JavaScript?</summary>
    <div class="wds-accordion__body">Búsqueda, filtrado de listas, y
      posicionamiento de tooltips en espacios estrechos. Están marcados como
      tales y no se han falseado.</div></details>

  <h3>Formularios</h3>
  <p class="spec"><code>.wds-field</code> <code>.wds-label</code>
    <code>.wds-input</code> <code>.wds-textarea</code> <code>.wds-select</code>
    <code>.wds-help</code> <code>.wds-error</code></p>
  <div style="max-width:26rem">
    <div class="wds-field">
      <label class="wds-label" for="f-mail">Correo</label>
      <input class="wds-input" id="f-mail" type="email" placeholder="tu@correo.com">
      <span class="wds-help">Nunca se comparte.</span>
    </div>
    <div class="wds-field">
      <label class="wds-label" for="f-topic">Tema</label>
      <select class="wds-select" id="f-topic">
        <option>Identidad</option><option>Sistema de diseño</option>
        <option>Otro</option>
      </select>
    </div>
    <div class="wds-field">
      <label class="wds-label" for="f-msg">Mensaje</label>
      <textarea class="wds-textarea" id="f-msg" rows="4"
        placeholder="Escribe aquí."></textarea>
      <span class="wds-help">Texto plano. Sin formato.</span>
    </div>
    <div class="wds-field">
      <label class="wds-label" for="f-bad">Campo con error</label>
      <input class="wds-input" id="f-bad" aria-invalid="true"
        aria-describedby="f-bad-err" value="no válido">
      <span class="wds-error" id="f-bad-err">Este valor no es válido.</span>
    </div>
  </div>

  <h3>Diálogo <span class="wds-badge">&lt;dialog&gt;</span></h3>
  <p class="spec"><code>.wds-dialog</code> — mostrado aquí con
    <code>open</code>. El modal real necesita <code>showModal()</code>: una
    línea de plataforma, no un framework, y es lo único que trae el
    <code>::backdrop</code> y la trampa de foco.</p>
  <dialog class="wds-dialog" open>
    <h4>Confirmar publicación</h4>
    <p>El activo se generará desde el CDS. No se edita a mano.</p>
    <div class="demo" style="margin-bottom:0">
      <button class="wds-btn wds-btn--primary">Generar</button>
      <button class="wds-btn wds-btn--ghost">Cancelar</button>
    </div>
  </dialog>

  <h3>Tooltip</h3>
  <p class="spec"><code>.wds-tooltip</code> · <code>__bubble</code> — sin motor
    de posicionamiento, así que solo etiquetas cortas en espacio abierto.
    Responde a <code>:hover</code> y a <code>:focus-within</code>.</p>
  <div class="demo" style="padding-top:var(--wds-space-8)">
    <span class="wds-tooltip">
      <button class="wds-btn wds-btn--secondary" aria-describedby="tt-1">Enfócame</button>
      <span class="wds-tooltip__bubble" role="tooltip" id="tt-1">Aparece también con teclado</span>
    </span>
  </div>

  <h3>Código</h3>
  <p class="spec"><code>.wds-code</code> — ancho limitado por
    <code>--wds-code-width</code>, no por el ancho de lectura.</p>
  <pre class="wds-code"><code>python build_wds.py
  consuming CDS 1.0.0 — B-PRIME-COMPENSATED
  identity digest verified: cf6b9fe5...
  colour contracts: 32/32 met</code></pre>
  <p>En línea, <code>code</code> se marca solo: el token
    <code>--wds-code-bg</code> lo separa del texto sin cambiar el ritmo.</p>

  <h3>Navegación</h3>
  <p class="spec"><code>.wds-breadcrumbs</code> · <code>.wds-pagination</code>
    · <code>.wds-nav-toggle</code></p>
  <ol class="wds-breadcrumbs">
    <li><a href="#main">Inicio</a></li>
    <li><a href="#components">Componentes</a></li>
    <li aria-current="page">Navegación</li>
  </ol>
  <nav class="wds-pagination" aria-label="Paginación">
    <a href="#components">&larr;</a>
    <a href="#components">1</a>
    <span aria-current="page">2</span>
    <a href="#components">3</a>
    <a href="#components">&rarr;</a>
  </nav>
  <p class="wds-caption">La navegación móvil es el
    <code>&lt;details class="wds-nav-toggle"&gt;</code> de la cabecera:
    invisible sobre 720&nbsp;px, disclosure nativo por debajo. Estrecha esta
    ventana para verlo cambiar.</p>

  <h3>Métricas</h3>
  <p class="spec"><code>.wds-metrics</code> · <code>.wds-metric__value</code>
    <code>.wds-metric__label</code></p>
  <div class="wds-metrics">
    <div><div class="wds-metric__value">110</div><div class="wds-metric__label">ACTIVOS</div></div>
    <div><div class="wds-metric__value">24/24</div><div class="wds-metric__label">REGRESIÓN</div></div>
    <div><div class="wds-metric__value">0</div><div class="wds-metric__label">JAVASCRIPT</div></div>
    <div><div class="wds-metric__value">5</div><div class="wds-metric__label">PARÁMETROS</div></div>
  </div>

  <h3>Línea de tiempo</h3>
  <p class="spec"><code>.wds-timeline</code></p>
  <ul class="wds-timeline">
    <li><strong>Fase IV</strong> — Canonical Design Specification congelada.</li>
    <li><strong>Fase V</strong> — Identity Production System, 110 activos.</li>
    <li><strong>Fase VI</strong> — Website Design System.</li>
  </ul>

  <h3>Estados</h3>
  <p class="spec"><code>.wds-empty</code> · <code>.wds-error-state</code>
    <code>.wds-skeleton</code> <code>.wds-progress</code></p>
  <div class="demo" style="align-items:stretch">
    <div class="wds-empty" style="flex:1;min-width:16rem">Nada que mostrar todavía.</div>
    <div class="wds-error-state" style="flex:1;min-width:16rem">No se pudo cargar.</div>
  </div>
  <div class="wds-stack" style="max-width:22rem">
    <div class="wds-skeleton" style="height:1rem"></div>
    <div class="wds-skeleton" style="height:1rem;width:70%"></div>
    <div class="wds-progress"><div class="wds-progress__bar" style="width:62%"></div></div>
  </div>

  <h3>Tipografía de contenido</h3>
  <p class="spec">Elementos base, sin clase: <code>blockquote</code>
    <code>hr</code> <code>ul</code> <code>kbd</code></p>
  <blockquote>No diseñes un logotipo. Diseña una idea tan clara que el
    logotipo parezca inevitable.</blockquote>
  <ul>
    <li>Las listas heredan el ancho de lectura.</li>
    <li>Un <kbd>Tab</kbd> recorre esta página entera sin saltarse nada.</li>
  </ul>
  <hr>

  <h3>El glifo</h3>
  <p class="spec"><code>.wds-glyph</code> · <code>.wds-mark</code> — consumido
    del CDS, nunca redibujado. El CSS solo lo dimensiona y lo sienta en la
    línea base.</p>
  <p class="wds-mark" style="font-size:var(--wds-text-h2)">{glyph}<strong>arjuanfelipe</strong></p>

  <h3>Utilidades</h3>
  <p class="spec"><code>.wds-visually-hidden</code> ·
    <code>.wds-skip-link</code> · <code>.wds-reading</code> ·
    <code>.wds-section</code> · <code>.wds-stack</code> ·
    <code>.wds-container</code></p>
  <p>El enlace de salto es el primer elemento de la página: pulsa
    <kbd>Tab</kbd> desde arriba y aparece.
    <span class="wds-visually-hidden">Este texto solo existe para lectores de
      pantalla.</span> Antes de esta frase hay un texto oculto visualmente pero
    presente en el árbol de accesibilidad.</p>
  <div class="wds-section" style="padding-block:var(--wds-space-6)">
    <p class="wds-reading">Un bloque <code>.wds-section</code> con un párrafo
      <code>.wds-reading</code>: ritmo vertical y medida, los dos por token.</p>
  </div>
"""


def build_docs(tok, col, cds, rows, css_text):
    glyph = _glyph(cds)

    type_rows = "".join(
        f'<tr><td><code>--wds-text-{n}</code></td>'
        f'<td class="num">{mn:.1f}px</td><td class="num">{mx:.1f}px</td>'
        f'<td style="font-size:var(--wds-text-{n});line-height:1.2">'
        f'Now {glyph} understand.</td></tr>'
        for n, mn, mx, _ in type_scale(tok))

    contrast_rows = "".join(
        f'<tr><td>{r["theme"]}</td><td><code>{r["fg"]}</code></td>'
        f'<td><code>{r["bg"]}</code></td><td class="num">{r["ratio"]:.2f}</td>'
        f'<td class="num">{r["target"]}</td><td>{r["level"]}</td></tr>'
        for r in rows)

    unit = tok["spacing"]["unit_px"]
    space_rows = "".join(
        f'<div class="sp"><span class="sp__bar" style="width:{s*unit}px">'
        f'</span><code>--wds-space-{s}</code>'
        f'<span class="sw__num">{s*unit}px</span></div>'
        for s in tok["spacing"]["steps"] if s)

    grid_cells = "".join(f"<div>{i+1}</div>" for i in range(12))
    nav_links = ('<a href="#color">Color</a><a href="#type">Tipografía</a>'
                 '<a href="#space">Espacio</a>'
                 '<a href="#components">Componentes</a>'
                 '<a href="#a11y">Accesibilidad</a>')

    return f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paleta canónica — WDS · arjuanfelipe</title>
<meta name="description" content="Website Design System de arjuanfelipe: paleta canonica, escala tipografica, rejilla y componentes, derivados del CDS.">
<!-- The stylesheet is inlined, not linked: this page must survive being moved. -->
<style>
{css_text}
{DOC_CSS}</style>
</head>
<body>
<a class="wds-skip-link" href="#main">Saltar al contenido</a>

<header class="wds-header"><div class="wds-container wds-header__inner">
  <span class="wds-mark">{glyph}<strong>arjuanfelipe</strong></span>
  <nav class="wds-nav" aria-label="Documentación">
    {nav_links}
  </nav>
  <details class="wds-nav-toggle">
    <summary aria-label="Abrir navegación">Menú</summary>
    <nav class="wds-nav" aria-label="Documentación (móvil)">
      {nav_links}
    </nav>
  </details>
</div></header>

<main id="main" class="doc">

<section>
  <div class="wds-hero">
    <p class="eyebrow">WEBSITE DESIGN SYSTEM · v{tok['wds_version']}</p>
    <h1 class="wds-hero__title">Now {glyph} understand.</h1>
    <p class="wds-hero__lead">El lenguaje operativo con el que la identidad se
      comunica. Consume el CDS {cds['cds_version']}; no lo modifica.</p>
    <div class="demo" style="margin-bottom:0">
      <span class="wds-badge">CERO JS</span>
      <span class="wds-badge">DARK-FIRST</span>
      <span class="wds-badge wds-badge--success">{len(rows)}/{len(rows)} CONTRASTE</span>
      <span class="wds-badge wds-badge--info">CDS {cds['path']['sha256'][:8]}</span>
    </div>
  </div>
</section>

<section id="color">
  <p class="eyebrow">01 — COLOR</p>
  <h2>Todo deriva de la paleta canónica.</h2>
  <p>Los colores semánticos son el accent canónico rotado en matiz dentro de
    OKLCH, manteniendo luminancia y croma. Por eso el contraste es constante
    por construcción, no por ajuste.</p>
  <div class="demo">
    <span class="wds-badge wds-badge--success">SUCCESS</span>
    <span class="wds-badge wds-badge--warning">WARNING</span>
    <span class="wds-badge wds-badge--danger">DANGER</span>
    <span class="wds-badge wds-badge--info">INFO</span>
  </div>
  <div class="wds-callout wds-callout--warning">
    <span class="wds-callout__label">Límite</span>
    <div><strong>danger</strong> queda a solo
      {col['meta']['min_hue_separation']['degrees']:.1f}° de <strong>primary</strong>.
      Con un accent naranja, un rojo de peligro no puede separarse más sin salir
      de la familia. Nunca deben aparecer adyacentes sin etiqueta de texto.</div>
  </div>
  <h3>Tokens (dark)</h3>
  {_swatches(col, 'dark')}
</section>

<section id="type">
  <p class="eyebrow">02 — TIPOGRAFÍA</p>
  <h2>Escala modular {tok['type_scale']['ratio']}, fluida entre {tok['type_scale']['fluid_viewport_min_px']} y {tok['type_scale']['fluid_viewport_max_px']} px.</h2>
  <p>El cuerpo de texto no encoge en móvil; solo los títulos comprimen, y cuanto
    más grandes, más comprimen.</p>
  <div class="wds-table-wrap"><table class="wds-table">
    <thead><tr><th>token</th><th class="num">mín</th><th class="num">máx</th><th>muestra</th></tr></thead>
    <tbody>{type_rows}</tbody>
  </table></div>
</section>

<section id="space">
  <p class="eyebrow">03 — ESPACIO Y REJILLA</p>
  <h2>Base 4. Ningún valor arbitrario.</h2>
  <div class="scroller">{space_rows}</div>
  <h3>Rejilla de {tok['grid']['columns']} columnas</h3>
  <div class="wds-grid grid-demo">{grid_cells}</div>
  <p class="wds-caption">En móvil colapsa a 4 columnas. Ancho de lectura
    limitado a {tok['grid']['reading_max_ch']}ch; bloques de código a
    {tok['grid']['code_max_ch']}ch.</p>
</section>

<section id="components">
  <p class="eyebrow">04 — COMPONENTES</p>
  <h2>Construidos sobre HTML nativo.</h2>
  <p>Todo lo que define <code>components.css</code> aparece abajo. No por
    disciplina: el build falla si una clase existe en la hoja de estilos y no
    se muestra en esta página.</p>
{_components(glyph)}
</section>

<section id="a11y">
  <p class="eyebrow">05 — ACCESIBILIDAD</p>
  <h2>Cada par verificado por cálculo.</h2>
  <p>Ningún color entra en el sistema por su aspecto. Todos los contratos de
    contraste se resuelven en el build y detienen la compilación si fallan.</p>
  <div class="wds-table-wrap"><table class="wds-table">
    <thead><tr><th>tema</th><th>frente</th><th>fondo</th><th class="num">ratio</th><th class="num">mín</th><th>nivel</th></tr></thead>
    <tbody>{contrast_rows}</tbody>
  </table></div>
</section>

</main>

<footer class="wds-footer"><div class="wds-container">
  WDS v{tok['wds_version']} · consume CDS {cds['cds_version']} ·
  glifo {cds['identity']['canonical_glyph']} · generado, no escrito a mano.
</div></footer>
</body>
</html>
"""
