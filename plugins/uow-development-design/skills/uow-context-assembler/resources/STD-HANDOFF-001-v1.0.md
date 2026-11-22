---
type: STD
id: STD-HANDOFF-001
title: "COMSATEL — Estándar de Readiness y Handoff entre Skills Packs"
description: "Contrato corporativo para evaluar la preparación de entregables compuestos y autorizar su transferencia entre packs y hacia Desarrollo."
version: "1.0.0"
status: draft
classification: internal
owner: "team:software-architecture"
tags: [comsatel, handoff, readiness, dtc, governance, sdlc]
generated:
  by: "process:standards-authoring"
  at: "2026-10-18T00:00:00Z"
sources: []
---

# STD-HANDOFF-001 — Readiness y Handoff entre Skills Packs

> **Estado:** Propuesta final para revisión y aprobación. **Ámbito:** Skills Packs de COMSATEL, especialmente Requirements, UX/UI, Architecture, DTC, Database, Microservices y Development. Los ejemplos son sintéticos y no acreditan aprobaciones reales.

## 1. Propósito

Definir un contrato verificable, interoperable y auditable para decidir si un **alcance de implementación** puede transferirse entre packs o entregarse a Desarrollo. Un artefacto con `status: stable` es documentalmente vigente, pero **no acredita** por sí mismo preparación para Sprint ni para desarrollo.

## 2. Principios obligatorios

1. **Separación de estados:** `status` del frontmatter OKF describe ciclo de vida documental (`draft`, `stable`, `deprecated`); readiness y gates son estados operativos independientes.
2. **Handoff compuesto:** se evalúa un alcance explícito —una US, varias US o una funcionalidad— junto con las versiones de sus artefactos y criterios de aceptación.
3. **Aplicabilidad contextual:** UX/UI, API, PDM, migraciones, arquitectura y seguridad se exigen cuando corresponden; la no aplicabilidad requiere evidencia y justificación.
4. **Fail-closed:** ausencia de evidencia, incompatibilidad de versiones, cobertura incompleta o gate fallido bloquean el avance.
5. **Orquestador soberano:** únicamente el orquestador autoriza ejecución de especialistas, registra estados oficiales, evalúa gates y emite autorizaciones de handoff.
6. **Intervención humana:** cualquier gate `BLOCKED` o `FAIL` obligatorio detiene las tareas dependientes y exige decisión humana registrada, seguida de reevaluación; no existe aprobación automática por simple cambio manual de estado.
7. **Procedencia y gobierno:** enlaces a Stitch, Claude Design y Figma no equivalen a aprobación; el diseño gobernado debe identificarse por versión y evidencia de revisión.
8. **Reproducibilidad:** cada evaluación registra IDs, versiones, revisiones/commits, evidencias y política aplicada.

## 3. Relación con STD-OKF-001

Los documentos `.md` de KB mantienen frontmatter OKF v0.2 con `type` como sigla del catálogo corporativo, `id`, `title`, `description`, `version`, `status`, `sources`, `generated` y otros campos del perfil COMSATEL. **No** se añaden `sprint_ready`, `development_ready` ni estados mutables de gates a sus frontmatters. Los planes y estados operativos se almacenan en YAML. Los archivos `index.md` y `log.md` de OKF conservan su tratamiento especial.

## 4. Estados y semántica

| Objeto | Estados permitidos | Significado |
|---|---|---|
| Documento OKF | `draft`, `stable`, `deprecated` | Madurez y vigencia documental |
| Tarea | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`, `FAILED` | Ejecución del plan |
| Gate | `PENDING`, `PASS`, `FAIL`, `BLOCKED`, `WAIVED`, `NOT_APPLICABLE` | Resultado de evaluación |
| Handoff | `DRAFT`, `EVALUATING`, `BLOCKED`, `AUTHORIZED`, `REVOKED` | Autorización de transferencia |

`WAIVED` requiere autorización humana, alcance, vigencia y riesgo aceptado. `NOT_APPLICABLE` requiere justificación y evidencia de que el criterio no corresponde al alcance. **Ninguno de los dos se interpreta automáticamente como `PASS`.** La política de cada gate define si un waiver explícito es admisible.

## 5. Unidades de evaluación y gates

- **REQUIREMENTS_READY:** criterios de aceptación, reglas, trazabilidad y alcance funcional aprobados.
- **UX_READY:** UXR, FLW, SCR, estados, accesibilidad y diseño gobernado cuando aplican.
- **TECHNICAL_DESIGN_READY:** API, errores, arquitectura, datos, seguridad e integraciones según el alcance.
- **SPRINT_READY:** requisitos, dependencias aplicables, estimación, riesgos y disponibilidad de planificación.
- **DEVELOPMENT_READY:** handoff completo y consistente hacia Developer + agente IA + Superpowers.

Un gate no debe confundirse con la definición de hecho de una tarea ni con el ciclo de vida de un documento.

## 6. Estructura operativa estándar

```text
./comsatel/dtc/
├── plan.yaml
├── plan-status.yaml
├── execution-report.md
├── tasks/
│   └── T-01/
│       └── task-status.yaml
├── gates/
│   └── development-ready.yaml
└── handoffs/
    └── CL2-US-010/
        ├── handoff-manifest.yaml
        ├── handoff-status.yaml
        └── handoff-report.md
```

Para otros packs se sustituye `dtc` por `[pack-name]`. El plan y sus estados se gobiernan por el orquestador; los especialistas producen artefactos y evidencias, no autorizaciones finales.

## 7. Contrato de `handoff-manifest.yaml`

```yaml
schema_version: "1.0"
handoff_id: DTC-HO-CL2-US-010
pack: dtc
scope:
  type: user_story
  ids: [CL2-US-010]
  acceptance_criteria: [AC-01, AC-02, AC-03]
source: DTC
target: DEVELOPMENT
policy: STD-HANDOFF-001@1.0.0
required_artifacts:
  - type: US
    id: CL2-US-010
    version: "1.0.0"
    required: true
    coverage: [AC-01, AC-02, AC-03]
  - type: UXR
    id: CL2-UXR-010
    required: true
    coverage: [AC-01, AC-02]
  - type: FLW
    id: CL2-FLW-010
    required: true
    coverage: [AC-01, AC-02]
  - type: SCR
    id: CL2-SCR-010
    required: true
    governed_design:
      provider: figma
      url: null
      revision: null
      approval_evidence: null
  - type: API
    id: CL2-API-010
    required: true
    coverage: [AC-01, AC-03]
  - type: PDM
    id: CL2-PDM-010
    required: true
    coverage: [AC-03]
applicability:
  database_migration:
    required: false
    rationale: "Ejemplo: no se modifican estructuras persistentes"
  mobile_ui:
    required: false
    rationale: "Ejemplo: alcance exclusivamente web"
criteria:
  - id: COVERAGE
    mandatory: true
  - id: UX_GOVERNANCE
    mandatory: true
  - id: API_CONTRACT
    mandatory: true
  - id: DATA_CONSISTENCY
    mandatory: true
  - id: TRACEABILITY
    mandatory: true
  - id: APPROVALS
    mandatory: true
```

Las referencias reales deben incluir `resource` o ruta, commit/revisión inmutable, versión y evidencia verificable. Los campos `null` anteriores **bloquean** autorización hasta completarse. No debe asumirse que API y PDM son siempre obligatorios: el orquestador determina aplicabilidad por alcance.

## 8. Contrato de `handoff-status.yaml`

```yaml
schema_version: "1.0"
handoff_id: DTC-HO-CL2-US-010
execution_id: DTC-EXEC-001
status: BLOCKED
last_evaluated_at: "2026-10-18T16:00:00Z"
gate:
  id: DEVELOPMENT_READY
  status: BLOCKED
  criteria:
    COVERAGE: PASS
    UX_GOVERNANCE: BLOCKED
    API_CONTRACT: PENDING
    DATA_CONSISTENCY: PENDING
    TRACEABILITY: PENDING
    APPROVALS: PENDING
  blocking_reasons:
    - code: DESIGN_APPROVAL_MISSING
      artifact_id: CL2-SCR-010
      detail: "Falta revisión y versión del diseño Figma gobernado"
  human_intervention:
    required: true
    request_id: HITL-001
    decision: PENDING
  authorization: null
```

Los estados se actualizan a partir de verificaciones reales, nunca de suposiciones. Una autorización emitida debe incluir `authorized_by`, `authorized_at`, `scope`, `evidence_refs`, `policy_version` y un identificador verificable; queda invalidada cuando cambian versiones relevantes o se revoca una aprobación.

## 9. Contrato de control del orquestador

1. Crear `plan.yaml` y `plan-status.yaml` y validar **G0** antes de lanzar especialistas.
2. Resolver DAG y evaluar gates de dependencias; bloquear tareas sucesoras cuando exista gate obligatorio sin `PASS` o excepción autorizada explícitamente.
3. Emitir autorización por tarea (`task_id`, `skill_id`, `execution_id`, `input_versions`, `gate_snapshot`, `expires_at`).
4. El runtime ejecutor **debe verificar** esa autorización antes de invocar el skill; un registro YAML por sí solo no impide invocaciones fuera de banda.
5. Recibir outputs/evidencias, ejecutar validadores deterministas y revisión semántica pertinente.
6. Evaluar gate y registrar evento de auditoría. En `BLOCKED`/`FAIL`, solicitar intervención humana y detener dependientes.
7. Tras resolución humana, **reevaluar** el gate y emitir nueva autorización; no reusar permisos antiguos.
8. Emitir handoff únicamente cuando todos los criterios obligatorios aplicables satisfagan la política.

## 10. Matriz mínima de validación del DTC Handoff

| Criterio | Evidencia mínima | Bloqueo típico |
|---|---|---|
| Cobertura funcional | US, AC y matriz AC→artefacto | AC sin solución trazable |
| UX/UI | UXR, FLW, SCR, diseño gobernado | Pantalla sin versión Figma aprobada |
| API | OpenAPI, endpoints, errores, seguridad | Contrato inconsistente o faltante |
| Datos | PDM y migración si aplica | Esquema o cambio no aprobado |
| Arquitectura | ADR/ASR y límites cuando aplican | Decisión crítica sin resolver |
| Integraciones | Contratos y fallas externas | Dependencia no definida |
| Consistencia | Referencias cruzadas y versiones | US, UX y API contradictorios |
| Gobierno | Evidencias, aprobaciones y gates | Ausencia de autoridad de aprobación |

## 11. Casos de prueba de aceptación

- **US stable sin UX:** `SPRINT_READY` y `DEVELOPMENT_READY` deben permanecer `BLOCKED` cuando UX es obligatorio.
- **SCR con URL Figma sin aprobación:** `UX_GOVERNANCE=BLOCKED`.
- **Backend sin UI:** `UX_READY=NOT_APPLICABLE` con justificación verificable; no bloquear por pantallas inexistentes.
- **PDM stable pero API contradictoria:** `DEVELOPMENT_READY=BLOCKED`.
- **G0 bloqueado:** no se ejecuta ningún especialista sucesor; registrar solicitud humana.
- **Cambio de versión después de autorización:** revocar handoff y reevaluar.
- **Waiver humano:** registrar identidad, motivo, alcance, riesgo y vencimiento; nunca convertir automáticamente a `PASS`.
- **Skill intenta autoprobar gate:** rechazar transición.

## 12. Integración con COMSATEL Skill Pack Factory

Todo pack generado debe declarar: entradas/salidas por `type` del catálogo, contratos por skill, gates, criterios, política de no aplicabilidad, handoffs ofrecidos/consumidos y pruebas negativas. Se mantiene el máximo predeterminado de **6 especialistas + 1 orquestador**, con excepción justificada y aprobada. Cada skill se distribuye independientemente con `SKILL.md`, `assets/`, `scripts/`, `resources/` y sus dependencias necesarias. Preferir redacción LLM-first y scripts deterministas para extracción, validación, control y verificación; no proliferar generadores de documentos sin beneficio medido.

## 13. Adopción y versionado

1. Conciliar el catálogo real de tipos con las KB y MCP existentes.
2. Versionar `STD-OKF-001` y `STD-HANDOFF-001` en un repositorio corporativo de estándares.
3. Incorporar plantillas y validadores a Skill Pack Factory y DTC Pack.
4. Ejecutar pruebas E2E de bloqueo, intervención humana, reanudación y revocación.
5. Publicar mediante MR, con trazabilidad de aprobaciones y rollback.

**Nota:** esta especificación define el contrato objetivo. No implica que los runtimes de agentes, GitLab, Stitch, Claude Design, Figma o MCP ya estén integrados o validados.
