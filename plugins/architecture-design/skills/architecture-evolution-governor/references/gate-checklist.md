# Checklist G5

- [ ] Inputs y versiones identificados
- [ ] Fuentes reales y afirmaciones clasificadas
- [ ] Artefactos Markdown pasan validador STD-OKF-001 v1.11.0-stable
- [ ] Contradicciones, riesgos y preguntas abiertas visibles
- [ ] Dependencias y decisiones humanas registradas
- [ ] Aprobación humana documentada; nunca inferida del script

## Política de rutas
Consultar `assets/pathmap.md` de la raíz del plugin: entregables especializados en `./architecture/` (ADR `adrs/`, ASR `asrs/`); solo el orchestrator escribe control en `.comsatel/architecture-design/runs/<run-id>/`. Overrides únicamente por instrucción explícita.
