---
name: biz-scenario-modeler
description: Modelar escenarios de negocio (BSN) como secuencias de reglas BR con precondiciones, pasos, excepciones y resultado, trazados a BR, TRM, BCAP y BO. Usar para BSN; escenario de negocio; business scenario.
metadata:
  version: "0.1.0"
---

# Business Scenario Modeler

## Activación
Usar cuando se requiera producir `BSN`. Puede ejecutarse individualmente con sus precondiciones. Este skill no planifica ni aprueba gates; el orchestrator decide su encadenamiento.

## Entradas obligatorias
Reglas `BR` aprobadas o en revisión para el alcance del escenario, términos `TRM` del glosario, y la capacidad `BCAP` y el objetivo `BO` a los que responde el escenario. Revisar `references/contract.md`; no suponer que una regla o un término existen sin verlos en `business/`.

## Procedimiento
1. Delimitar el actor, la capacidad, el disparador, el alcance y el resultado esperado del escenario.
2. Elegir las reglas BR que intervienen en cada paso. Si falta una regla, registrar una pregunta abierta; no inventar reglas.
3. Redactar el documento a partir de `templates/scenario.md`, con las once secciones del contrato y en el mismo orden.
4. Clasificar cada afirmación como hecho, inferencia, supuesto, hipótesis, decisión o vacío (sección 9).
5. Ejecutar `python scripts/check_scenario.py <archivo.md> --workspace <raíz>` y `python scripts/validate.py <archivo.md>`.
6. Entregar el borrador con readiness READY, CONDITIONAL o NOT_READY. La aprobación la da una persona; este skill no aprueba.

## Salidas
Un `business/scenarios/BSN-NNN-<slug>.md` por escenario. Las evidencias de ejecución, en `.comsatel/business-knowledge/runs/<run-id>/`.

## Trazabilidad
Cada paso del escenario referencia una `BR` por ID. El escenario declara en `related` las `BR`, `TRM`, `BCAP` y `BO` que usa. Las reglas siguen viviendo en `business/rules/`; el escenario no las redefine.

## Restricciones
- No inventar actores, reglas, estados ni excepciones que no estén en las fuentes.
- No asignar `verified` ni `stable` sin autorización explícita.
- `status: draft` mientras no haya aprobación humana.
- No crear commits, MR ni publicar sin autorización explícita.
- Si falta un insumo, registrar el bloqueo y una pregunta.

## Contrato de conformidad documental
- El tipo `BSN` está registrado en STD-OKF-001 v0.1.0-stable.
- La validación no equivale a aprobación humana ni a publicación.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto (`business/scenarios/`) con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato. Ver `references/output-path-policy.md`.
