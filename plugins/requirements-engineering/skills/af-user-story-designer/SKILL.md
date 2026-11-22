---
name: af-user-story-designer
description: Refinar User Stories individuales, INVEST, backlog e identificación HU. Usar para HU por archivo; backlog-delta; INVEST.
metadata:
  version: "0.1.0"
---

# af-user-story-designer

## Activación
Usar cuando refinar user stories individuales, invest, backlog e identificación hu. Puede ejecutarse individualmente con sus precondiciones o por `af-requirements-orchestrator`.

## Entradas obligatorias
RCP, reglas BR (G2) y catálogo HUC. La línea base de negocio (`business/`: BR, IMD, TRM, BCP y BO) la produce el plugin `business-knowledge`: citarla por ID en `related` y `sources`, sin redefinirla. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Delimitar producto, iniciativa, alcance y consumidor del resultado.
2. Inspeccionar fuentes autorizadas y versionadas; registrar provenance y clasificación de cada afirmación.
3. Consultar `references/technical-guidance.md`.
4. Asignar el ID de cada historia con `python scripts/us_ids.py next --workspace <raíz> --rcp RCP-NNN [--count N] [--also <otra-KB>] --git-ref origin/develop` (ver «IDs de User Stories» abajo); nunca elegir el número a mano ni reutilizar el de otra historia. Luego, elaborar artefactos conforme a `references/okf-v1.3-profile.md` y `templates/deliverable.md`; preservar los templates originales de cada capacidad.
5. Verificar completitud, contradicciones, fuentes, preguntas, owners y trazabilidad, y ejecutar `python scripts/us_ids.py check --workspace <raíz> --git-ref origin/develop` (más `--also` por cada otra KB y `--git-ref` por cada rama abierta): debe terminar con 0 errores.
6. Ejecutar `scripts/validate.py` sobre el documento, emitir evidencia y solicitar aprobación humana G3.

## IDs de User Stories (globalmente únicos)
- **Formato:** `RCP-NNN-US-NNN`, donde `RCP-NNN` es el ID del RCP que origina la historia; `NNN` son tres o más dígitos correlativos dentro de ese RCP. Ejemplo: `RCP-002-US-014`.
- **Código de producto:** metadato opcional `product` en MAYÚSCULAS (`CL2`, `CL2-BAS`, `SG`...). No forma parte del ID.
- **Archivo:** `<ID>.md` o `<ID>-<slug>.md`, un archivo por historia, en `requirements/context-packs/user-stories/`.
- **Inmutable y no reutilizable:** el ID nunca se renumera ni se reasigna, ni siquiera si la historia se retira (pasa a `status: deprecated`). `HU-NN-NN` y los `US-001` heredados se conservan en el campo `legacy_id`.
- **Por qué el prefijo de origen:** un número solo (`US-001`) se repite entre paquetes y KB, y el ID es el `concept_id` que enlaza con el issue de GitLab (`gitlab-work-publisher`); una colisión fusionaría o sobrescribiría historias distintas.
- **Asignación y verificación:** `scripts/us_ids.py next --rcp RCP-002` asigna el siguiente número de ese RCP; `check` detecta formato inválido, archivo que no coincide con el ID e IDs duplicados. `--also` suma otras KB y `--git-ref` suma ramas o tags del repositorio, que es donde ocurre la colisión real: dos personas numerando en paralelo. La asignación es local, sin servidor central: la unicidad entre ramas se garantiza ejecutando `check --git-ref` antes de cada integración, en G3 y de nuevo en G6.
- **Código de producto:** si se informa, debe ser único entre todas las KB; registrar uno nuevo es una decisión de gobierno, no del skill. Si dos KB usan el mismo código, `check --also` no lo detecta: es un metadato, así que la revisión humana lo confirma.

## Épicas (EPC)
- **Propósito:** agrupar historias funcionalmente relacionadas del mismo RCP bajo un resultado de negocio. Plantilla: `templates/epic.md`.
- **Formato:** `RCP-NNN-EPC-NNN`, con el mismo RCP de origen que sus historias. Numeración propia de épicas; `us_ids.py next` no la cuenta para las US.
- **Archivo:** `<ID>.md` o `<ID>-<slug>.md`, en `requirements/context-packs/epics/`.
- **Pertenencia:** la épica declara sus historias en `related`; la US no lleva campo de épica. Una US pertenece como máximo a una épica. Una historia sin épica es válida.
- **Criterio de agrupación obligatorio:** sin él la épica no es válida. Sus criterios de aceptación de extremo a extremo se trazan a criterios de las historias incluidas; no introduce requisitos nuevos.
- **Validación:** `validate_okf.py` exige el ID y `related`; `us_ids.py check` verifica que las US citadas existan y que ninguna esté en dos épicas.

## Salidas
US por archivo; EPC por archivo (opcional); backlog delta e INVEST devueltos como payload al orchestrator. Publicar borradores bajo `requirements/` en la KB de producto; payloads de ejecución devueltos al orchestrator; solo el orchestrator persiste evidencias y estado bajo `.comsatel/requirements-engineering/runs/<run-id>/`.

## Gate G3
Estado `READY`, `CONDITIONAL` o `NOT_READY` **no equivale a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no habilitar tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar actores, reglas, dependencias, prioridades, comportamientos ni criterios de aceptación.
- Diferenciar hechos, inferencias, supuestos, hipótesis, vacíos y decisiones humanas.
- Una User Story por archivo. El ID es `RCP-NNN-US-NNN` y es globalmente único (ver `af-user-story-designer`); un ID previo (`HU-NN-NN`, `US-001`) va en `legacy_id`, no en `id`. Reutilizar preguntas y EVD existentes.
- Markdown OKF v0.2 con STD-OKF-001 vigente; no asignar `verified` ni `stable` sin autorización.
- No crear commits, MR ni publicar KB sin autorización explícita.
- Si el input requerido no existe, registrar bloqueo y pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate_okf.py <archivo.md>` desde la raíz del plugin (o el wrapper local `scripts/validate.py`).
- El resultado de validación no equivale a aprobación humana ni a publicación. En `--publication`, rechazar tipos no aprobados y metadatos inválidos.
- Aplicar STD-OKF-001 v0.1.0-stable como perfil objetivo; usar el catálogo aprobado de la versión vigente.
- Para outputs operativos JSON/YAML en `.comsatel/`, usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas (v1.5.0)
Leer `../../assets/pathmap.md` desde el directorio del skill (o `assets/pathmap.md` desde la raíz del plugin). Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` del frontmatter contra el contrato y guardar en el destino resuelto. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato. Nunca escribir documentos especializados en `.comsatel/`. Ejecutar validación OKF v0.1.0-stable.
