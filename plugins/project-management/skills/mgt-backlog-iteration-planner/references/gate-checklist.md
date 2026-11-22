# Checklist G2

- [ ] Fuentes y provenance verificables
- [ ] Alcance y exclusiones explícitos
- [ ] Criterio de priorización declarado y Definition of Ready evaluada por historia; las que no cumplen quedan en Excluye
- [ ] Criterios de cierre del Sprint verificables en GitLab
- [ ] Estimación de referencia hecha con `estimate.py` (v3): `/time`, `/cost`, `/time_agent` y `/cost_agent` presentes; QA calculado desde los TC manuales y automatizados de `qa-design`; avisos revisados, historias XL divididas y tipo de cambio informado por una persona (o `/cost_agent` en `PENDIENTE`)
- [ ] Coeficientes de QA y agente declarados en la sección «Referencia de esfuerzo y costo» como aprobados y pendientes de calibración, hasta cerrar el primer Sprint
- [ ] Sin fechas, costos, capacidad ni umbrales inventados
- [ ] IDs y trazabilidad cruzada consistentes
- [ ] Decisiones humanas registradas con quién y cuándo
- [ ] Contradicciones, preguntas y owners registrados
- [ ] OKF v0.2 y STD-OKF-001 aplicados (`scripts/validate.py`)
- [ ] Evidencia del gate registrada (`templates/gate-evidence.json`)
- [ ] Aprobación humana identificada (no autoaprobación)

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
