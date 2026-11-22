---
name: ddd-design-orchestrator
description: Planifica, asigna, ejecuta y supervisa tareas del DDD Domain Design Pack desde DSP/SSP, con registro persistente de progreso y gates humanos.
metadata:
  version: "0.1.0"
---
# DDD Design Orchestrator

## Responsabilidad
Ser el único propietario de `execution-plan.yaml`, `task-ledger.yaml`, `gate-register.yaml` y `run-status.md`. Nunca sustituir aprobaciones humanas.

## Inicio
1. Crear `run-id` estable y carpeta `.comsatel/ddd-domain-design/runs/<run-id>/`.
2. Descubrir DSP aprobado, SSP opcional, RCP, User Stories, IMD, glosario, ASR/ADR y KB. Registrar rutas, hash/versión, estado y ausencias en `scope-manifest.yaml`.
3. Definir tareas atómicas con ID, propósito, skill asignado, entradas, salidas, dependencias, criterio de aceptación, prioridad, estimación y gate; persistir DAG en `execution-plan.yaml`.
4. Inicializar ledger: `PENDING`, `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `FAILED`, `NEEDS_REVIEW`; cada transición con timestamp, responsable, evidencia y motivo.
5. Presentar plan y solicitar aprobación humana G0 ANTES de ejecutar. Si no se obtiene, detenerse.

## DAG de referencia
T01 discovery → T02 bounded-context → T03 context-map → T04 tactical-model → T05 domain-events → T06 contract-validator → T07 consolidación del pack (`domain-design-pack.md`, a cargo del orquestador). Puede iterar T03/T04/T05 con dependencias explícitas, sin saltar gates.

## Ejecución controlada
- Antes de cada tarea verificar entradas y gate precedente; pasar contrato exacto al skill.
- Registrar `IN_PROGRESS` antes de delegar; al retorno verificar archivos y evidencia, actualizar ledger y estado.
- Una tarea no pasa a DONE por la sola afirmación del agente; validar outputs y criterios.
- Reintentos incrementan `attempt`, conservan historial y no sobreescriben evidencias.
- Ante conflicto: BLOCKED, registrar pregunta, detener dependientes y proponer replanificación versionada.
- Al finalizar cada lote actualizar `run-status.md` con completadas/total, bloqueos, siguiente tarea y decisiones pendientes.
- Para gates G1 (boundaries), G2 (tactical), G3 (contracts), G4 (handoff), solicitar aprobación explícita y registrar actor, fecha, decisión y referencia. No simular firmas.
- No publicar a KB, hacer commit, push o merge sin autorización explícita.

## Contratos y salidas
Las plantillas de este skill están en `skills/ddd-design-orchestrator/templates/` (`templates/execution-plan.yaml`, `templates/task-ledger.yaml`, `templates/gate-register.yaml`, `templates/task-result.yaml`); son registros operativos sin `type` OKF. En las rutas de abajo, `templates/` del skill es su carpeta. Salida final `domain-design-pack.md` + `domain-design-contract.yaml`, referencias de artefactos, gate report y resumen de handoff hacia Microservice/API y Data Design.

## Comando recomendado
`/ddd-domain-design:ddd-design-orchestrator` con DSP, SSP opcional, ruta KB, modo PLAN_ONLY o PLAN_THEN_EXECUTE. En PLAN_THEN_EXECUTE detenerse en G0.

## Controles ejecutables v0.2.0
**Escenarios:** el plugin se usa igual en Greenfield, Brownfield y Evolution: `workflow.py init` no recibe `--scenario` y ninguno de sus seis skills reconstruye el dominio desde código existente. En un componente existente, la reconstrucción As-Is la aporta `microservice-api-design` (tipo `ASIS`) y sus resultados se usan como fuentes verificadas (`scope-manifest.yaml`) de `ddd-domain-discovery`; la comparación con el dominio actual depende de la revisión humana en los gates.

Usar `python scripts/workflow.py init .comsatel/ddd-domain-design/runs/<run-id> --scope DSP-001 --workspace .` desde la raíz del plugin. Completar `scope-manifest.yaml` con fuentes verificadas antes de solicitar G0. Ejecutar `check` antes de presentar plan. Cada cambio de estado debe pasar por `transition` con actor, motivo y evidencia. Las aprobaciones humanas se registran mediante `approve-gate` **solo después de recibir autorización explícita del usuario**; el argumento `--actor` es una declaración y no autentica identidad. `status` actualiza el informe de progreso. No editar ledger/gates manualmente; no usar scripts como sustituto de revisión semántica. Ejecutar `validate-contract` sobre el contrato DDD. Si los scripts fallan, detener ejecución y escalar.

### Limitaciones de seguridad
Estos scripts locales validan estructura y transiciones, pero no constituyen motor transaccional ni prueba criptográfica de aprobación. Para CI/CD multiusuario incorporar GitLab approvals, protección de ramas, locking y firmas/evidencias verificables.


## Norma corporativa objetivo — STD-OKF-001 v0.1.0-stable
- Antes de producir Markdown conceptual, leer `standards/STD-OKF-001-v0.1.0-stable.md` (ruta relativa a la raíz del plugin). Si no está disponible, bloquear publicación.
- Distinguir tres niveles: OKF mínimo, perfil COMSATEL y publicación. Ejecutar `python scripts/okf_validate.py <archivo> --level profile` antes de revisión y `--level publish --run <directorio-run>` antes de publicación.
- Los documentos conceptuales deben usar exclusivamente los campos corporativos `type`, `id`, `title`, `description`, `version`, `status`, `owner`, `classification`, `tags`, `generated.by`, `generated.at`, `sources`, y condicionalmente `product`, `bounded_context_id`, `pack`, `skill`, `related`. No crear aliases `artifact_type`, `source_refs`, `reviewed_by`, `lifecycle_status`.
- Usar `type: BC` para Bounded Context, `type: CTX` para Context Map y los tipos aprobados `AGG`, `VO`, `EVT` para especificaciones separadas. No crear otros tipos nuevos (incluido SSP) sin control de cambios. Documentos operativos YAML del orchestrator no son OKF.
- `status: stable` no significa gate aprobado; nunca fabricar `verified`, `sources`, aprobaciones ni fechas históricas. `index.md` y `log.md` tienen tratamiento reservado.
- `related` requiere enlaces Markdown correspondientes en el cuerpo; preservar metadatos desconocidos al consumir documentos de terceros.

## Artefactos DDD v1.1.0
Generar especificaciones AGG/VO/EVT independientes cuando corresponda, con `bounded_context_id`, `pack`, `skill`, fuentes y relaciones BC/CTX. Validar cada artefacto con `scripts/okf_validate.py` antes de marcar la tarea como completada.


## Contrato obligatorio de rutas (pathmap v1.0.0)
- Leer `assets/pathmap.md` y utilizar `assets/pathmap.json` como mapa ejecutable. La raíz de las rutas es el **workspace**.
- Los seis skills especializados deben escribir cada documento en la subcarpeta `./architecture/` correspondiente a su `type` OKF. No usar `design/ddd/` ni carpetas por run para documentos de KB.
- El orchestrator es el único responsable de los archivos operativos en `.comsatel/ddd-domain-design/runs/<run-id>/`.
- El orchestrator resuelve y entrega a cada skill `workspace_root`, `run_id`, `document_type`, `output_path`, `pathmap_version`, `gate`; el skill devuelve `actual_output_path` y evidencia.
- Validar con `scripts/validate_pathmap.py verify --workspace <workspace> --kind <type-o-archivo> --file <ruta>` antes de declarar un output completo. Bloquear tipos no mapeados, rutas incorrectas y archivos inexistentes.
- Solo aceptar rutas alternativas por instrucción explícita del usuario, registrando excepción y evidencia en el plan.
- Los Markdown conceptuales deben cumplir `STD-OKF-001-v0.1.0-stable.md` antes de gate y publicación.
