# Checklist G4

- [ ] Fuentes y provenance verificables
- [ ] Alcance y exclusiones explícitos
- [ ] Contenido sin invenciones; hechos separados de supuestos
- [ ] IDs y trazabilidad cruzada consistentes
- [ ] Contradicciones, preguntas y owners registrados
- [ ] OKF v0.2 y STD-OKF-001 aplicados (`scripts/validate.py`)
- [ ] Evidencia del gate registrada (`templates/gate-evidence.json`)
- [ ] Aprobación humana identificada (no autoaprobación)

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
