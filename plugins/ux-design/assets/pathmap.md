# UX Design — política de rutas

`pathmap.json` es la única fuente para decidir rutas canónicas por tipo. El orchestrator lo carga al iniciar cada run y comunica el tipo, destino y gate a cada skill.

## Documentos conceptuales

- `UXR`, `FLW`, `SCR`, `CMP`, `TKN`, `ADR`, `CFR` y `HOF` usan `document_types`.
- `CTLG` requiere `catalog_role`; solo se permiten roles declarados en `catalog_role_routes`. `design-traceability-map` indexa SCR y conserva su lineage; `component-inventory` indexa CMP.
- El ID del frontmatter debe ser estable, único y prefijo del nombre del archivo. `related` debe contener IDs con enlaces Markdown en el cuerpo cuando corresponda.
- La ruta no se deduce del nombre de archivo ni del skill. No sobrescribir artefactos existentes sin instrucción/versionado explícito.
- `US` y `RCP` son entradas de solo lectura del pack; este plugin no los crea ni cambia.

## Gestión y payloads

La planificación, escenarios, modo de ciclo de vida, ledger, estados, gates, referencias externas Stitch/Figma, prompts, briefs de exploración y propuestas de gate se guardan bajo `.comsatel/ux-design/runs/<run-id>/`. Estos datos son operativos, no llevan frontmatter OKF y no sustituyen los documentos conceptuales en `design/`.

Los skills especialistas escriben documentos únicamente en la ruta canónica del `type` resuelta por este mapa. Sus payloads operativos solo se guardan en el run cuando el contrato del orchestrator lo indica. Ningún skill modifica el `gate-register.json` ni aprueba gates.

## Excepciones

Un tipo sin mapping o un `catalog_role` desconocido queda bloqueado. Un override requiere instrucción explícita del usuario y se registra en el run con ruta original, ruta resuelta, justificación y actor declarado.
