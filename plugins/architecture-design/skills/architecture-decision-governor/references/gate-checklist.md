# Checklist G3

- [ ] Inputs y versiones identificados
- [ ] Fuentes reales y afirmaciones clasificadas
- [ ] Artefactos Markdown pasan validador STD-OKF-001 v0.1.0-stable
- [ ] Contradicciones, riesgos y preguntas abiertas visibles
- [ ] Dependencias y decisiones humanas registradas
- [ ] Cada ADR tiene diagrama Mermaid o "Visual: no aplica — <motivo>" aceptado por el arquitecto
- [ ] Catálogo de elementos cubre todos los IDs `E-nn` del diagrama, con descripción y marca de punto de variación
- [ ] Cada punto de variación `VP-nn` tiene dimensión, variantes, momento de vinculación y responsable
- [ ] Evaluación ATAM con sensibilidades, compromisos, riesgos y no-riesgos, o justificación de tipo vacío
- [ ] Escenarios de calidad `QA-nn` con medida de respuesta con fuente o `[PENDIENTE: arquitecto]`
- [ ] `scripts/validate.py` pasa en frontmatter y cuerpo; el Mermaid renderiza si se ejecutó `--render`
- [ ] Aprobación humana documentada; nunca inferida del script

## Política de rutas
Consultar `assets/pathmap.md` de la raíz del plugin: entregables especializados en `./architecture/` (ADR `adrs/`, ASR `asrs/`); solo el orchestrator escribe control en `.comsatel/architecture-design/runs/<run-id>/`. Overrides únicamente por instrucción explícita.
