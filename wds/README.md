# WDS — Website Design System · arjuanfelipe

El lenguaje operativo con el que la identidad se comunica.

```
CDS  ->  IPS  ->  WDS  ->  componentes  ->  páginas
```

El WDS **consume** la identidad. Nunca la modifica.

En este repositorio lee `../identity/cds.json` —la especificación real, no una
copia— en solo lectura, y verifica su digest en cada build. Si el CDS no está o
ha derivado, la compilación se detiene. Una segunda copia del CDS podría
divergir, que es justo lo que el CDS existe para impedir.

## Uso

```bash
python build_wds.py      # deriva tokens, valida contraste, emite CSS y docs
python validate_wds.py   # 20 comprobaciones de integridad del sistema
```

Ambos salen con 0. Sin dependencias externas: solo la stdlib de Python 3.

## Salida

| Archivo | |
|---|---|
| `css/tokens.css` | custom properties: color, tipo, espacio, motion, z-index |
| `css/base.css` | reset y elementos base |
| `css/components.css` | 30+ componentes, cero JS |
| `css/wds.css` | punto de entrada único (28,8 KB · **6,1 KB gzip**) |
| `docs/index.html` | documentación viva, **auto-contenida** (64 KB) |
| `../paleta_canonica/paleta_canonica.html` | el mismo render, byte a byte |
| `tokens.resolved.json` | export para herramientas |
| `WDS-RELEASE.json` | hashes por artefacto + digest de release |

La documentación **incrusta** el CSS en vez de enlazarlo. Un `href` relativo
solo resuelve desde la carpeta para la que se escribió: mover la página la deja
sin un solo estilo, y sin ningún error. Se emite un único render a los dos
destinos, los dos con hash en el manifiesto —una copia hecha a mano ya se quedó
obsoleta una vez.

El build es determinista byte a byte: dos ejecuciones producen el mismo
`release_digest`. Un digest distinto sin un cambio deliberado significa que
algo se rompió.

## Reglas

- Ningún color se escribe a mano en una hoja de estilos: todos derivan del
  accent canónico y se validan por cálculo.
- Ningún espaciado arbitrario: todo sale de la escala base-4.
- Cero JavaScript. Lo que lo necesitaría está declarado en `DECISIONS.md`.
- El glifo se consume del CDS; el WDS no contiene geometría.
- Ningún componente queda sin documentar: el build falla si una clase existe en
  la hoja de estilos y no aparece en la página (test T16).

## Antes de usarlo

`DECISIONS.md` cierra con lo que **no** está verificado. Lo esencial: la página
se ha abierto y recorrido en Chromium —y eso destapó tres defectos que ningún
test de cálculo veía (WDS-010)— pero **no en Firefox ni en Safari**, y nadie la
ha escuchado con un lector de pantalla.
