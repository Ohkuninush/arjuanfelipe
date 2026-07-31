# identity — B′ · COMPENSATED

Especificación de ingeniería del glifo canónico de **arjuanfelipe**.

La fuente de verdad es `cds.json`. Todo lo demás se genera.

```
cds.json  →  geometry.py  →  build/master.svg  →  activos derivados
```

## Uso

```bash
python validate.py      # 24 comprobaciones de regresión
python third_party.py   # prueba de completitud: reconstruye solo desde cds.json
python generate.py      # regenera los 20 activos en build/
```

Los tres deben salir con código 0. Sin dependencias externas: solo la
biblioteca estándar de Python 3.

## Reglas

- **Nunca edites un SVG a mano.** Son artefactos compilados. Se regeneran.
- **Nunca derives un activo de otro activo.** Todo sale del CDS.
- **Nunca cambies la geometría canónica** sin una Design Decision formal que
  supere la anterior con evidencia objetiva. Ver `CDS.md` §14.
- `build/` es desechable. Bórralo y regenéralo cuando quieras: el build es
  determinista byte a byte.

## Estado

| | |
|---|---|
| CDS versión | 1.0.0 |
| Glifo | `B-PRIME-COMPENSATED` |
| Estado | FROZEN, 2026-07-30 |
| SHA-256 del path | `cf6b9fe5350776e6514853257925c045b339370c3485d471dca5acaa314d3ad3` |
| Decisiones congeladas | DD-001 … DD-010 |

## Antes de usar esto en producción, lee

Dos decisiones tienen **confianza BAJA** y están señaladas como tales en
`CDS.md` §12:

- **DD-008** — la elección del candidato B se hizo por selección, no por
  evidencia. La pregunta perceptual que habría discriminado entre las tres
  variantes nunca se respondió.
- **DD-009** — el grosor de asta `77.31` es normativo **por congelación, no por
  derivación**: su método no converge. Re-ejecutarlo no reproduce el valor.

Y un defecto conocido que se embarca sin corregir: **DEF-001**, el codo se lee un
8 % más denso que el asta. Corregirlo rompería DD-002.

Las métricas de composición (`metrics` en `cds.json`) están marcadas
**PROVISIONAL**: dependen de la tipografía del sistema y no se han medido contra
una fuente real en ninguna plataforma.
