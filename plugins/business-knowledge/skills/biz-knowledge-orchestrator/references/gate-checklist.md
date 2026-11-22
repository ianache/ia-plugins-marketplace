# Gates

G0: alcance y fuentes autorizadas. G1: contexto y objetivos trazables. G2: actores y capacidades vinculados a objetivos. G3: glosario con fuentes y 0 errores de `glossary.py check`. G4: reglas con origen y términos enlazados. G5: modelo conceptual sin errores de `check_model.py`. G6: `check_pack.py` sin errores, trazabilidad y handoff.

No aprobar automáticamente ni inferir la identidad del revisor.

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
