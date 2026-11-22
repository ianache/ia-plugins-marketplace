---
name: solution-ideation-orchestrator
description: Usar para planificar, coordinar y gobernar ideación e innovación de soluciones nuevas o existentes, activando seis skills especializados, contratos y gates antes del handoff a requirements-engineering.
metadata:
  version: "0.1.0"
---

# Solution Ideation Orchestrator

## Objetivo
Maximizar exploración creativa y aprendizaje validable sin confundir ideación con requisitos aprobados. Coordinar seis skills; no ejecutar todo por defecto ni reemplazar su especialización.

## Activación y escenarios
- **Greenfield**: oportunidades → problemas → divergencia → conceptos → experimentos → handoff.
- **Brownfield**: recuperar As-Is y evidencia del producto antes de replantear oportunidades.
- **Evolution**: contrastar hipótesis y compatibilidad con capacidades existentes; conservar alternativas.
- **Exploración aislada**: puede generar ideas sin handoff; documentar gates omitidos y motivo, no simular aprobación.

## Ejecución
1. Recibir objetivo, audiencia, producto, problema inicial y fuentes. Registrar incertidumbres y criterios de innovación.
2. Crear `.comsatel/solution-ideation/runs/<run-id>/` con `execution-plan.json`, `state.json`, `gate-register.json`, hipótesis y backlog de ideas.
3. Aplicar G0: scope, contexto, límites éticos y autorización para investigar/experimentar.
4. Asignar a cada skill el contrato en `references/workflow-contract.md`, y comprobar evidencia de salida.
5. En G1–G5 solicitar revisión humana cuando proceda; `READY` técnico no equivale a `approved`.
6. Solo activar `innovation-requirements-handoff` con concepto seleccionado por humano y evidencia o incertidumbre explícita; bloquear G6 si falta decisión.
7. Entregar a `requirements-engineering` una propuesta SOL en borrador + `handoff.json` y fuentes, **no** User Stories aprobadas ni RCP ficticio. El receptor reconstruye RCP y valida requisitos.

## Gates
G0 iniciativa y alcance; G1 oportunidades; G2 problem framing; G3 diversidad creativa; G4 conceptos y alternativas; G5 experimentos y riesgos; G6 handoff aceptable.

## Documentos y gobierno
- Operativos y control: `.comsatel/solution-ideation/runs/<run-id>/`.
- Propuestas conceptuales OKF: `design/ideation/<run-id>/`, `type: SOL` (Solution Proposal, aprobado en v0.1.0-stable; una sola sigla para todas las etapas, indicada en `ideation_stage`). No crear otras siglas sin gobierno.
- STD-OKF-001 v0.1.0-stable es perfil objetivo; no fingir que es estable. Ejecutar `scripts/validate_okf.py` y registrar resultados.
- No publicar, fusionar MRs ni aprobar gates automáticamente. Identidad humana en JSON es declaración, no autenticación.

## Recursos
`references/workflow-contract.md`, `references/gate-checklist.md`, `references/technical-guidance.md`, `templates/`, `scripts/`, `examples/`, `assets/`.
