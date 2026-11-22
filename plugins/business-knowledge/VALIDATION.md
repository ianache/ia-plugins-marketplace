# Validación v1.0.0

- Ocho skills (1 orchestrator y 7 especializados) con recursos propios y wrappers de validación.
- Perfil OKF y plantillas alineados a STD-OKF-001 v1.9.0-stable, incluidos los tipos aprobados `TRM`, `BCP`, `BO`, `STK`, `BCAP`, `BSN`.
- Validador común: YAML, campos, enums, SemVer, `generated.at`, `sources`, tipo, campos condicionales (`product`, `pack`, `skill`) y cuerpo no vacío.
- `glossary.py` (glosario), `check_model.py` (modelo conceptual) y `check_pack.py` (conjunto) son verificaciones deterministas de estructura.
- Tests: `python -m unittest discover -s tests -v` (requiere PyYAML).
- Limitaciones: no verifica contenido semántico, veracidad de fuentes ni autorización humana; la sintaxis Mermaid solo se comprueba si hay `npx` y `mermaid-cli`; no hay validación real dentro de Claude Code.
