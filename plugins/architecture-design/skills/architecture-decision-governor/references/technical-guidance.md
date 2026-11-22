# Guía técnica — architecture-decision-governor

Mantener las disciplinas originales como subprocedimientos dentro de este skill, no como skills adicionales publicados. Preservar las perspectivas Applications, Integration, Data, Infrastructure; ASR quality scenarios; ADR lifecycle; conformance, drift, fitness, governance y knowledge curation según aplique. Separar baseline As-Is de To-Be. No asumir herramientas ni repositorios disponibles.

## ATAM ligero por ADR
Cada ADR registra el resultado de una evaluación ATAM reducida a la decisión (no sustituye una sesión ATAM con stakeholders):
1. Drivers de negocio y restricciones, con fuente (`## Contexto y drivers`).
2. Escenarios de calidad de seis partes: fuente, estímulo, artefacto, entorno, respuesta y medida (`## Escenarios de calidad afectados`). La medida sin fuente va como `[PENDIENTE: arquitecto]`; no se inventan objetivos.
3. Opciones consideradas, incluida la de no hacer nada.
4. Evaluación: **sensibilidad** (la decisión afecta a un solo atributo), **compromiso** (mejora un atributo y degrada otro), **riesgo** (puede no cumplir un escenario) y **no-riesgo** (se evaluó y cumple). Cada registro referencia un `QA-nn` existente.

## Sección visual y puntos de variación
- **Diagrama:** `flowchart` para estructura y despliegue, `sequenceDiagram` para flujos, `stateDiagram-v2` para ciclos de vida. Todo ADR tiene al menos un diagrama. Si no aplica, `Visual: no aplica — <motivo>`.
- **IDs:** cada nodo o participante tiene `E-nn`; el mismo ID aparece en el catálogo. Cada punto de variación tiene `VP-nn`, en la tabla y en el diagrama (clase `vp` o nota).
- **Punto de variación:** elemento cuyo comportamiento o configuración cambia entre variantes (entorno, proveedor, producto, tenant, versión o tecnología de despliegue). Se registra el momento de vinculación (diseño, construcción, despliegue o ejecución) y el responsable. Un elemento que no varía se marca `No`.
- **Sintaxis:** etiquetas entre comillas (`E01["Servicio (único)"]`); no usar `end` como ID; `<br/>` para saltos de línea. Verificar con `scripts/validate.py --render` en local.

## Política de rutas
Consultar `assets/pathmap.md` de la raíz del plugin: entregables especializados en `./architecture/` (ADR `adrs/`, ASR `asrs/`); solo el orchestrator escribe control en `.comsatel/architecture-design/runs/<run-id>/`. Overrides únicamente por instrucción explícita.

## Enrutamiento obligatorio
Usar el contrato `document_type`/`output_dir` emitido por el orchestrator y el `assets/pathmap.md` de la raíz del plugin; bloquear rutas no mapeadas.
