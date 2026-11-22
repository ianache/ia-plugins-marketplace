# Checklist G3

- [ ] Fuentes y provenance verificables
- [ ] Alcance y exclusiones explícitos
- [ ] Reglas y conclusiones sin invenciones
- [ ] IDs y trazabilidad cruzada consistentes
- [ ] ID de cada US = `RCP-NNN-US-NNN`, asignado con `us_ids.py next --rcp`, sin reutilizar y con `us_ids.py check` en 0 errores (también con `--git-ref` de ramas abiertas y `--also` de otras KB)
- [ ] IDs previos (`HU-NN-NN`, `US-001`) conservados en `legacy_id`
- [ ] Si hay épicas: ID `RCP-NNN-EPC-NNN`, cada `related` apunta a una US existente y ninguna US está en dos épicas
- [ ] Si hay épicas: criterio de agrupación explícito y cada criterio de la épica trazado a criterios de sus historias
- [ ] Contradicciones, preguntas y owners registrados
- [ ] OKF v0.2 y STD-OKF-001 aplicados
- [ ] Evidencia del gate registrada
- [ ] Aprobación humana identificada (no autoaprobación)

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
