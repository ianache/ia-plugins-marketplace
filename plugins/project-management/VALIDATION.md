# Validación v2.1.0

- Siete skills (1 orchestrator y 6 especializados) con recursos propios y wrappers de validación.
- Perfil OKF y plantillas alineados a STD-OKF-001 v1.9.0-stable, incluidos los tipos aprobados `PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`.
- Validador común: YAML, campos, enums, SemVer, `generated.at`, `sources`, tipo, campos condicionales (`product`, `pack`, `skill`) y cuerpo no vacío.
- `check_management.py` verifica el conjunto: OKF, rutas, enlaces, IDs de `related`, `CHG` sin decisión y `RSK` sin dueño.
- Tests: `python -m unittest discover -s tests -v` (requiere PyYAML).
- `gitlab_milestone.py` se prueba con un GitLab simulado en memoria (idempotencia, aprobación humana, redacción del PAT, no cierra ni elimina); no se ha probado contra una instancia real salvo que se indique en una verificación aparte.
- `gitlab_issues.py` y `estimate.py` se prueban con un GitLab simulado y con la fórmula de la práctica v2 (ejemplo de la práctica: 22 h); los coeficientes de QA y del agente están aprobados por el PO pero sin calibrar con datos históricos.
- Limitaciones: no verifica veracidad de cifras, horas, KPI ni autorización humana; los skills externos (`gsd-*`, GitLab, informes) no se ejecutan en los tests; no hay validación real dentro de Claude Code ni contra una instancia de GitLab.
