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
python validate_wds.py   # 15 comprobaciones de integridad del sistema
```

Ambos salen con 0. Sin dependencias externas: solo la stdlib de Python 3.

## Salida

| Archivo | |
|---|---|
| `css/tokens.css` | custom properties: color, tipo, espacio, motion, z-index |
| `css/base.css` | reset y elementos base |
| `css/components.css` | 30+ componentes, cero JS |
| `css/wds.css` | punto de entrada único (27,9 KB · **5,9 KB gzip**) |
| `docs/index.html` | documentación viva, generada |
| `tokens.resolved.json` | export para herramientas |
| `WDS-RELEASE.json` | hashes por artefacto + digest de release |

El build es determinista byte a byte: dos ejecuciones producen el mismo
`release_digest`. Un digest distinto sin un cambio deliberado significa que
algo se rompió.

## Reglas

- Ningún color se escribe a mano en una hoja de estilos: todos derivan del
  accent canónico y se validan por cálculo.
- Ningún espaciado arbitrario: todo sale de la escala base-4.
- Cero JavaScript. Lo que lo necesitaría está declarado en `DECISIONS.md`.
- El glifo se consume del CDS; el WDS no contiene geometría.

## Antes de usarlo

`DECISIONS.md` cierra con lo que **no** está verificado. Lo esencial: esta hoja
de estilos no se ha abierto en ningún navegador ni se ha probado con lector de
pantalla. La validación es estructural, no visual.
