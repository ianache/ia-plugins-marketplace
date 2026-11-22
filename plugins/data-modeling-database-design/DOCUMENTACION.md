# Data Modeling & Database Design — Documentación del plugin

Diseña el modelo de datos y la base de datos de un servicio: reconstrucción As-Is, ownership de datos por contexto, modelo lógico, modelo físico, migraciones Flyway y validación. Usa **un orquestador y seis skills especialistas**, con gates de aprobación humana.

- **Versión:** 1.3.0 · **Documentos:** STD-OKF-001 v1.11.0-stable
- **Entrada:** modelo conceptual, RCP/DSP/SSP, DDD (`BC`, `CTX`, `AGG`, `VO`, `EVT`), FDT, contratos OpenAPI, ADR y codebase con DDL/Flyway.
- **Salida:** documentos en `design/database/<run-id>/`; controles en `.comsatel/data-modeling-database-design/runs/<run-id>/`.

---

## 1. Skills

| Skill | Gate | Qué hace | Entregable |
| :--- | :-: | :--- | :--- |
| `dm-design-orchestrator` | — | Determina el escenario, crea la corrida, asigna tareas, valida salidas y evidencias. | `execution-plan.json`, `gate-register.json`, `scope-manifest.json` |
| `dm-schema-reconstruction-analyzer` | G1 | Reconstruye el modelo As-Is desde DDL, catálogos, Flyway, ORM y código; registra evidencia, incertidumbre y drift. | `as-is/database-reconstruction.md` (`DBR`) |
| `dm-data-boundary-designer` | G2 | Ownership de datos por BC y servicio, esquema, multitenancy, integración entre contextos y excepciones ADR. | `to-be/logical-data-model.md` (sección de ownership del LDM tipado) |
| `dm-logical-model-designer` | G3 | Modelo lógico: cardinalidad, claves, invariantes y trazabilidad a DDD y FDT. | `to-be/logical-data-model.md` (`LDM`) |
| `dm-physical-model-designer` | G4 | Estructuras del motor: tipos, tablas, índices, constraints, rendimiento y seguridad. | `to-be/physical-data-model.md` (`PDM`) |
| `dm-database-migration-designer` | G5 | Cambios Flyway/DDL: expand-contract, backfill, compatibilidad, rollout y rollback. En Greenfield, la migración inicial. | `migration/database-migration.md` (`DBM`) |
| `dm-data-design-validator` | G6 | Trazabilidad, consistencia LDM/PDM/DBM, ADR, FDT, tenancy, seguridad y evidencia. | `validation/data-design-review.md` (`type: DDR`) |

Reglas comunes: no inventar esquemas, reglas ni evidencia (se registra un bloqueo); un bounded context no es un esquema ni un aggregate una tabla; no se publica ni se modifica un repositorio sin aprobación humana.

---

## 2. Escenarios y gates

Cada gate tiene un significado fijo. Cada escenario usa solo los que aplican, y una tarea entra por el gate de cierre de la anterior (G0 la primera).

| Escenario | Tareas | Gates |
| :--- | :--- | :--- |
| `greenfield` | ownership → lógico → físico → migración inicial → validación | G0, G2, G3, G4, G5, G6 |
| `brownfield` | reconstrucción → ownership → validación | G0, G1, G2, G6 |
| `evolution` | reconstrucción → ownership → lógico → físico → migración → validación | G0 a G6 |

| Gate | Significado | Se aprueba cuando |
| :-: | :--- | :--- |
| `G0` | Alcance y fuentes | `scope-manifest.json` tiene `sources` y `adr_refs` no vacíos. |
| `G1` | Reconstrucción As-Is | Tareas de G1 en `DONE` y el gate anterior del escenario aprobado. |
| `G2` | Ownership de datos | Ídem para G2. |
| `G3` | Modelo lógico | Ídem para G3. |
| `G4` | Modelo físico | Ídem para G4. |
| `G5` | Migración y compatibilidad | Ídem para G5. |
| `G6` | Validación y handoff: trazabilidad a FDT y fuentes, revisión de migraciones y rutas de handoff. | Ídem para G6. |

El gate anterior es el anterior que existe en el escenario (por ejemplo, G6 de Brownfield sigue a G2). El actor de la aprobación debe empezar por `human:` y se exige evidencia; el CLI no autentica al aprobador.

### Estados de una tarea

`PENDING` → `IN_PROGRESS` → `NEEDS_REVIEW` → `DONE`. Además `BLOCKED` y `FAILED`, que vuelven a `IN_PROGRESS`.

- Iniciar (`transition --to IN_PROGRESS`) exige el gate de entrada aprobado y las dependencias en `DONE`.
- Entregar (`--to NEEDS_REVIEW`) y cerrar (`complete`) exigen evidencia existente como archivo. `DONE` solo se alcanza desde `NEEDS_REVIEW`.
- Cada transición pide actor y motivo y queda en `history` de `execution-plan.json`.
- `execution-plan.json` lleva `schema_version`; una corrida con otra versión se rechaza con un mensaje que pide crear una nueva.

---

## 3. Documentos

| Sigla | Nombre | Lo produce | Archivo |
| :-: | :--- | :--- | :--- |
| `DBR` | Database Reconstruction | reconstruction-analyzer | `as-is/database-reconstruction.md` |
| `PDM` | Physical Data Model | physical-model-designer | `to-be/physical-data-model.md` |
| `DBM` | Database Migration | migration-designer | `migration/database-migration.md` |
| `LDM` | Logical Data Model (incluye ownership) | dm-data-boundary-designer + dm-logical-model-designer | `to-be/logical-data-model.md` |
| `DDR` | Data Design Review | dm-data-design-validator | `validation/data-design-review.md` |

El ownership se integra en el LDM tipado; la revision independiente es un DDR tipado. Ambos llevan `type`, `id` y el perfil documental completo de STD-OKF-001.

Plantillas: `templates/dbr-okf.md`, `ldm-okf.md`, `pdm-okf.md`, `dbm-okf.md`, `ddr-okf.md` y `data-handoff.yaml` (escenario, `schema_id`, destino en la KB, repositorio, destino de la migración por ADR, herramienta Flyway, aprobación humana y publicación por MR).

Registros operativos de `.comsatel/data-modeling-database-design/runs/<run-id>/`: `scope-manifest.json`, `execution-plan.json` y `gate-register.json`.

---

## 4. Dependencias entre documentos

`DBR → ownership → LDM → PDM → DBM → validación`, recortada según el escenario. Cada documento se apoya en el anterior de la cadena; todos reciben las mismas fuentes (DDD, FDT, ADR, codebase). El diseño lo consumen después los packs de desarrollo, por ejemplo `uow-development-design` (documento `UCB`).

---

## 5. Uso

```bash
python scripts/workflow.py init --workspace . --run-id DEMO --scenario evolution
python scripts/workflow.py check --workspace . --run-id DEMO
python scripts/workflow.py approve-gate --workspace . --run-id DEMO --gate G0 --actor human:reviewer --evidence MR-123
python scripts/workflow.py transition --workspace . --run-id DEMO --task T01 --to IN_PROGRESS --actor agent:dm --reason inicio
python scripts/workflow.py transition --workspace . --run-id DEMO --task T01 --to NEEDS_REVIEW --actor agent:dm --reason entrega --evidence path/to/evidence
python scripts/workflow.py complete --workspace . --run-id DEMO --task T01 --actor human:reviewer --evidence path/to/evidence
python scripts/workflow.py status --workspace . --run-id DEMO
```

---

## 6. Limitaciones conocidas

- La validación es estructural: no ejecuta los skills, no analiza bases reales ni valida SQL, Mermaid o semántica OKF.
- Los scripts no son seguros ante concurrencia ni prueban criptográficamente una aprobación.
