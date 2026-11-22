# DDD Domain Design — Documentación del plugin

Plugin de Claude Code que diseña el dominio con DDD (descubrimiento, bounded contexts, context map, modelo táctico y eventos) mediante **un orquestador y seis skills especialistas**. Cada paso queda registrado y está protegido por **gates con aprobación humana**.

- **Versión:** 1.2.0 · **Autor:** COMSATEL Engineering
- **Entrada:** DSP aprobado (SSP opcional), RCP, User Stories, IMD, glosario, ASR/ADR y KB.
- **Salida:** `domain-design-pack.md` + `domain-design-contract.yaml`, para los packs de Microservicios/API y Data Design.
- **Invocación:** `/ddd-domain-design:ddd-design-orchestrator`

---

## 1. Skills

| # | Skill | Rol | Tarea | Entregable principal |
| :-: | :--- | :--- | :-: | :--- |
| 0 | `ddd-design-orchestrator` | Planifica, asigna, supervisa y registra. Único dueño de `execution-plan`, `task-ledger`, `gate-register` y `run-status`. No ejecuta lógica de dominio ni aprueba gates. | T07 | `domain-design-pack.md` + `domain-design-contract.yaml` (consolida el pack) |
| 1 | `ddd-domain-discovery` | Descubre dominios y subdominios: landscape, Core/Supporting/Generic, lenguaje ubicuo, evidencias y preguntas abiertas. | T01 | `domain-discovery.md` (`ACP`) |
| 2 | `ddd-bounded-context-designer` | Delimita bounded contexts: l?mites sem?nticos, capacidades, owners, reglas, responsabilidades y alternativas. | T02 | `bounded-contexts.md` (`CTLG`, ?ndice `BC`) |
| 3 | `ddd-context-map-designer` | Dise?a el Context Map: upstream/downstream, ACL, OHS, Published Language, Customer/Supplier, Conformist y justificaci?n. | T03 | `context-map.md` (`CTX`) |
| 4 | `ddd-tactical-model-designer` | Dise?a el modelo t?ctico: aggregates y ra?ces, entities, value objects, invariantes, servicios y transacciones. | T04 | `tactical-model.md` (`CTLG`, ?ndice `AGG`) |
| 5 | `ddd-domain-event-designer` | Dise?a comandos y domain events, diferenci?ndolos de los eventos de integraci?n: ownership, sem?ntica y versionado. | T05 | `domain-events.md` (`CTLG`, ?ndice `EVT`) |
| 6 | `ddd-domain-contract-validator` | Valida consistencia DDD y contratos: hallazgos, trazabilidad, cobertura y conflictos. Recomienda gates sin autoaprobar. | T06 | `domain-design-contract.yaml` + `CFR-domain-validation.md` |

Reglas comunes a los seis especialistas:

- Leen solo fuentes disponibles y declaran las ausentes. No inventan contenido del DSP, SSP, RCP, ADR, User Stories ni KB.
- El DSP gobierna el alcance. El SSP organiza el trabajo y no lo amplía.
- No editan artefactos de otros skills ni aprueban gates. Emiten hallazgos y piden revisión humana.
- No asumen que bounded context = microservicio, aggregate = tabla ni domain event = evento de integración.
- Si faltan insumos críticos la tarea queda `BLOCKED`. `DONE` no significa aprobado.

---

## 2. Secuencia de ejecución

```mermaid
flowchart LR
  G0{{G0 Alcance}} --> T01[T01 discovery]
  T01 --> T02[T02 bounded contexts]
  T02 --> T03[T03 context map]
  T03 --> G1{{G1 Límites}}
  G1 --> T04[T04 tactical model]
  T04 --> T05[T05 domain events]
  T05 --> G2{{G2 Táctico y eventos}}
  G2 --> T06[T06 contract validator]
  T06 --> G3{{G3 Contratos}}
  G3 --> T07[T07 consolidación del pack]
  T07 --> G4{{G4 Handoff}}
```

| Tarea | Skill | Depende de | Gate de entrada | Gate de cierre |
| :-: | :--- | :--- | :-: | :-: |
| T01 | `ddd-domain-discovery` | — | G0 | G1 |
| T02 | `ddd-bounded-context-designer` | T01 | G0 | G1 |
| T03 | `ddd-context-map-designer` | T02 | G0 | G1 |
| T04 | `ddd-tactical-model-designer` | T02, T03 | G1 | G2 |
| T05 | `ddd-domain-event-designer` | T03, T04 | G1 | G2 |
| T06 | `ddd-domain-contract-validator` | T03, T04, T05 | G2 | G3 |
| T07 | `ddd-design-orchestrator` (consolidación) | T06 | G3 | G4 |

- **Gate de entrada:** debe estar aprobado para pasar la tarea a `READY` o `IN_PROGRESS`.
- **Gate de cierre:** la tarea debe estar `DONE` para poder aprobar ese gate.
- Una tarea nunca espera la puerta que ella misma debe cerrar. El gate de entrada es siempre el anterior al de cierre, y `workflow.py check` rechaza lo contrario con `gate cycle`.
- T03, T04 y T05 pueden iterar con dependencias explícitas, sin saltar gates.

**Estados de tarea:** `PENDING`, `READY`, `IN_PROGRESS`, `NEEDS_REVIEW`, `DONE`, `BLOCKED`, `FAILED`.
Transiciones permitidas:

- `PENDING` → `READY` o `BLOCKED`
- `READY` → `IN_PROGRESS` o `BLOCKED`
- `IN_PROGRESS` → `NEEDS_REVIEW`, `FAILED` o `BLOCKED`
- `NEEDS_REVIEW` → `DONE`, `FAILED` o `BLOCKED`
- `FAILED` y `BLOCKED` → `READY`

Una tarea solo llega a `DONE` desde `NEEDS_REVIEW`, con evidencia y con sus salidas existentes en la ruta del pathmap.

---

## 3. Entregables

### 3.1 Documentos de dominio (OKF, `STD-OKF-001`)

| Sigla | Nombre | Lo produce | Carpeta en el workspace |
| :-: | :--- | :--- | :--- |
| `BC` | Bounded Context | T02 | `architecture/bounded-contexts/` |
| `CTX` | Context Map | T03 | `architecture/context-maps/` |
| `AGG` | Aggregate | T04 | `architecture/domain-model/aggregates/` |
| `ENT` | Entity | T04 | `architecture/domain-model/entities/` |
| `VO` | Value Object | T04 | `architecture/domain-model/value-objects/` |
| `EVT` | Domain Event | T05 | `architecture/domain-events/` |

### 3.2 Documentos de síntesis por tarea

| Archivo | Tarea | Carpeta |
| :--- | :-: | :--- |
| `domain-discovery.md` (`ACP`) | T01 |
| `bounded-contexts.md` (`CTLG`, ?ndice `BC`) | T02 |
| `context-map.md` (`CTX`) | T03 |
| `tactical-model.md` (`CTLG`, ?ndice `AGG`) | T04 |
| `domain-events.md` (`CTLG`, ?ndice `EVT`) | T05 |
| `domain-design-contract.yaml` | T06 | `architecture/domain-contracts/` |
| `CFR-domain-validation.md` | T06 | `architecture/domain-contracts/` |
| `domain-design-pack.md` | T07 (orquestador) | `architecture/domain-contracts/` |

`domain-design-contract.yaml` es el contrato legible por máquina para los packs de API/Microservicios y Data. Debe contener: `bounded_contexts`, `context_relationships`, `aggregates`, `entities`, `value_objects`, `domain_events`, `integration_contract_candidates`, `source_refs`, `approval`. `validate-contract` valida estructura, patrones de relación (catálogo de Context Mapping), contexto propietario de entidades, VO y eventos, y que `approval: APPROVED` tenga actor, evidencia y gate G3 aprobado (`--run <carpeta-del-run>`). No sustituye la revisión semántica.

`CFR-domain-validation.md` es un documento `CFR` y pasa la validación `profile`/`publish`. `domain-design-pack.md` lo produce T07 (orchestrator), excluido del perfil documental.

### 3.3 Registros operativos del orquestador (no son OKF)

Van en `.comsatel/ddd-domain-design/runs/<run-id>/`:

- `execution-plan.yaml`: DAG de tareas, con entradas, salidas, gate de entrada y gate de cierre.
- `task-ledger.yaml`: estado, intentos, actor, evidencia e historial.
- `gate-register.yaml`: estado de G0–G4.
- `scope-manifest.yaml`: fuentes verificadas.
- `run-status.md`: progreso, bloqueos y gates pendientes.
- `task-results/<task-id>.yaml`: reporte de cada tarea.

---

## 4. Gates

| Código | Significado | Qué debe cumplirse para aprobarlo | Habilita |
| :-: | :--- | :--- | :--- |
| `G0` | **Alcance:** plan y fuentes aprobados antes de ejecutar. | `scope-manifest.yaml` con fuentes verificadas y sin `missing_sources`. | T01, T02, T03 |
| `G1` | **Límites de contexto:** discovery, bounded contexts y context map aceptados. | G0 aprobado; T01, T02 y T03 en `DONE`. | T04, T05 |
| `G2` | **Modelo táctico y eventos:** aggregates, entities, VOs y eventos aceptados. | G1 aprobado; T04 y T05 en `DONE`. | T06 |
| `G3` | **Contratos:** contrato DDD validado, consistente y trazable. | G2 aprobado; T06 en `DONE`. | T07 |
| `G4` | **Handoff:** pack final listo para Microservicios/API y Data Design. | G3 aprobado; T07 en `DONE`. | Publicación y consumo downstream |

Estados de un gate: `NOT_READY`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`.

- Los gates se aprueban en orden, G0 → G4.
- Aprobar exige `--actor` y `--evidence`. `--actor` es una declaración y no autentica identidad.
- Solo se ejecuta `approve-gate` tras autorización humana explícita. El agente nunca aprueba un gate.
- Antes de cada gate, cada skill cumple el checklist `references/gate-checklist.md`:
  - Inputs y fuentes verificadas.
  - Salida en la ruta asignada por el orquestador.
  - Frontmatter OKF válido.
  - IDs y referencias trazables.
  - Sin preguntas críticas abiertas.
  - Evidencia registrada y aprobación humana no simulada.

---

**Escenarios:** el plugin se usa igual en Greenfield, Brownfield y Evolution: `workflow.py init` no recibe `--scenario` y ninguno de sus seis skills reconstruye el dominio desde código existente. En un componente existente, la reconstrucción As-Is la aporta `microservice-api-design` (tipo `ASIS`) y sus resultados se usan como fuentes verificadas (`scope-manifest.yaml`) de `ddd-domain-discovery`; la comparación con el dominio actual depende de la revisión humana en los gates.

## 5. Uso del CLI local

```bash
python -m pip install PyYAML
W=<workspace>
python scripts/workflow.py init $W/.comsatel/ddd-domain-design/runs/RUN-001 --scope DSP-001 --workspace $W
# completar scope-manifest.yaml con fuentes verificadas
python scripts/workflow.py check  <run>
python scripts/workflow.py approve-gate <run> --gate G0 --actor 'human:<aprobador>' --evidence '<referencia>'
python scripts/workflow.py transition <run> --task T01 --to READY --actor orchestrator --reason 'G0 aprobado'
python scripts/workflow.py status <run>
python scripts/workflow.py validate-contract <ruta>/domain-design-contract.yaml
```

Validadores adicionales:

```bash
python scripts/okf_validate.py <archivo.md> --level profile      # antes de revisión
python scripts/okf_validate.py <archivo.md> --level publish --run <run>   # antes de publicar
python scripts/validate_pathmap.py verify --workspace <ws> --kind <tipo|archivo> --file <ruta>
```

Limitaciones: los scripts validan estructura y transiciones, no son concurrencia-seguros ni prueban criptográficamente una aprobación. Para uso multiusuario hay que integrar GitLab approvals y protección de ramas.

---

## 6. Observaciones resueltas

1. `CFR-domain-validation.md` se añadió al pathmap y T06 lo declara como segunda salida.
2. G4 tiene ahora tarea propia: T07 consolida `domain-design-pack.md`, con gate de entrada G3 y de cierre G4.
3. Las plantillas YAML usan `schema_version: '2.0'`, igual que el CLI. `skills/ddd-design-orchestrator/templates/execution-plan.yaml` sigue mostrando solo T01 como ejemplo.
