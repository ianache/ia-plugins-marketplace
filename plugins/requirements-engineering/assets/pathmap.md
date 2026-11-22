# Requirements Engineering — Workspace Output Pathmap

**Workspace root:** directorio de trabajo donde se invoca el plugin, no su directorio de instalación.  
**Alcance:** los cinco skills especializados y el orchestrator. Las reglas de negocio, el modelo de información y el glosario (`BR`, `IMD`, `TRM`) los produce el plugin `business-knowledge`; este pack los consume.

## Reglas obligatorias

1. El orchestrator debe leer este archivo al comenzar G0 y resolver cada entregable por `type` de su frontmatter OKF **antes de encargar su generación**.
2. Los entregables especializados van en los directorios que `pathmap.json` fija por tipo. La línea base de negocio (`./business/`, plugin `business-knowledge`) es de **solo lectura** para este pack: se referencia por ID y no se escribe aquí. Los archivos operativos creados por el orchestrator van exclusivamente a `<orchestrator_root>/<run-id>/` (la ruta base se obtiene del campo `orchestrator_root` de `pathmap.json`).
3. La ruta no se deduce del nombre del skill ni de la extensión; se deriva del tipo documental. No se admite un tipo sin mapping: **BLOCKED** hasta resolverlo y registrar la decisión.
4. Únicamente una instrucción explícita del usuario permite sobrescribir la ruta. El orchestrator registra texto original, ruta resuelta, actor, justificación y alcance; los skills no pueden autoautorizar excepciones.
5. No sobrescribir documentos existentes sin decisión explícita de evolución/versionado. Preservar links, IDs y provenance.
6. Cada skill debe validar `type`, `output_dir`, existencia y conformidad de frontmatter según `STD-OKF-001-v0.1.0-stable` antes de reportar un entregable listo. Solo se admiten tipos registrados en el estándar.
7. Los archivos JSON/YAML de evidencia o contratos de entrega de un skill especializado no son necesariamente documentos OKF; deben guardarse junto al entregable correspondiente bajo `./requirements/`, con una ruta explícita acordada en el contrato. Los registros de gates y planificación pertenecen al orchestrator.

## Mapeo por document type

El mapeo de cada tipo documental a su directorio (y los metadatos de cada artefacto) vive solo en [`pathmap.json`](pathmap.json), bajo `document_types` y `artifacts`; su versión está en `pathmap_version`. Este archivo no repite ese contenido.

**IDs de User Stories (`US`):** `RCP-NNN-US-NNN`, con `RCP-NNN` el ID del RCP que origina la historia (p. ej. `RCP-002-US-001`). El código de producto `product` (MAYÚSCULAS, p. ej. `CL2`) es un metadato opcional que no forma parte del ID. El ID es globalmente único, inmutable y no reutilizable; el archivo se llama `<ID>.md` o `<ID>-<slug>.md`; un ID previo (`HU-NN-NN`, `US-001`) va en `legacy_id`. `scripts/us_ids.py` asigna (`next`) y verifica (`check`, con `--also` para otras KB y `--git-ref` para ramas abiertas); `validate_okf.py` rechaza IDs de US que no sean `RCP-NNN-US-NNN`.

**Épicas (`EPC`):** `RCP-NNN-EPC-NNN`, con el mismo RCP de origen que sus historias, en `requirements/context-packs/epics/`. Numeración propia, separada de las US. La épica declara sus historias en `related`; una US pertenece como máximo a una épica. `us_ids.py check` verifica esas referencias.

**Línea base de negocio (consumida, no producida):** `BR` (`./business/rules/`), `IMD` (`./business/information-model/`) y `TRM` (`./business/terms/`) pertenecen a `business-knowledge` (pathmap propio). El gate G2 de este pack no genera documentos: se aprueba con evidencia del handoff G6 de ese pack o con una decisión humana explícita de continuar sin línea base. Los skills de este pack citan esos documentos por ID en `related` y `sources`.

Los JSON de análisis intermedio (`evidence-register`, `source-inventory`, `backlog-delta`, `acceptance-review`, `coverage`, `DoR`, `impact-surface-map`, `traceability-matrix` y `gate-report`) son payloads de ejecución, no documentos conceptuales Markdown. El especialista devuelve estos datos al orchestrator; solo el orchestrator los persiste bajo `<orchestrator_root>/<run-id>` (`.comsatel/requirements-engineering/runs/<run-id>/`). Los resultados aptos para consumo humano se incorporan a los artefactos OKF correspondientes: `impact-surface-map` en `IMP`, aceptación en `US`/`RCP`, y trazabilidad en `DSP`.

## Contrato orchestrator → skill

```json
{
  "run_id": "RUN-001",
  "workspace_root": ".",
  "skill": "af-user-story-designer",
  "document_type": "US",
  "output_dir": "<directorio del tipo en pathmap.json>",
  "pathmap_version": "<pathmap_version>",
  "override": null,
  "gate": "G3",
  "inputs": ["RCP-001"],
  "required_standard": "STD-OKF-001-v0.1.0-stable"
}
```

El skill devuelve un manifiesto de `document_type`, `actual_path`, `okf_validation`, `sources` y `gate_evidence`. El orchestrator valida ese manifiesto y bloquea gates si hay divergencias.

## Gates

- **G0:** cargar pathmap, registrar versión y generar contratos de rutas.
- **G1–G5:** validar los entregables de cada skill y bloquear tipos/rutas no resueltos.
- **G6:** revalidar todas las rutas y metadatos, verificar aprobación humana y preparar handoff sin publicar automáticamente.
