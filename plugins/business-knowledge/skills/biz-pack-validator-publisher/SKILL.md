---
name: biz-pack-validator-publisher
description: Validar coherencia y trazabilidad del conocimiento de negocio (OKF, rutas, índices, enlaces, IDs) y preparar el handoff gobernado. Usar para BCP final; trazabilidad; resultado de gate.
metadata:
  version: "0.1.0"
---

# Business Pack Validator & Publisher

## Activación
Usar cuando se requiera producir BCP final con sección de handoff (type BCP). Puede ejecutarse individualmente con sus precondiciones o por `biz-knowledge-orchestrator`. Solo el orchestrator planifica, despacha y evalúa gates; este skill no edita el plan ni el registro de gates.

## Entradas obligatorias
Todos los entregables de G1 a G5 en `business/` y sus gates aprobados. Revisar `references/contract.md`; no suponer que una salida anterior está aprobada.

## Procedimiento
1. Ejecutar `python scripts/check_pack.py --workspace <raíz>`: valida OKF y ruta de cada documento, los índices de BR y TRM, los enlaces entre documentos y que cada ID referenciado en `related` exista.
2. Revisar a mano lo que el script no verifica: coherencia semántica entre BO, BCAP, BR, TRM e IMD, contradicciones abiertas y preguntas sin responsable.
3. Construir la matriz de trazabilidad `BO -> BCAP -> BR -> IMD` (con TRM) como sección del handoff; listar huecos (reglas sin uso, conceptos sin término, objetivos sin capacidad).
4. Incorporar al BCP existente la seccion de handoff (usar `templates/handoff.md` como fragmento) con IDs, rutas, versiones, preguntas abiertas y consumidores: `requirements-engineering`, `ux-ui-design`, `architecture-design`, `ddd-domain-design` y `data-modeling-database-design`.
5. Emitir READY, CONDITIONAL o NOT_READY y solicitar aprobación humana del gate G6. No publicar, hacer commit ni merge de forma automática.

## Salidas
Actualiza el BCP tipado en `business/context-packs/` con inventario, trazabilidad, huecos, consumidores y readiness; devuelve resultados de gate estructurados al orchestrator, que es el unico que persiste gate-report y evidencias operativas.

## Límites de la validación
`check_pack.py` verifica estructura, rutas, índices, enlaces e IDs; no certifica veracidad de fuentes, semántica ni aprobación humana. Con STD-OKF-001 v0.1.0-stable estos tipos están aprobados y ya no se emiten avisos `type propuesto`.

## Gate G6
READY, CONDITIONAL y NOT_READY **no equivalen a aprobación**. Una persona autorizada aprueba el gate; sin aprobación no se habilitan tareas dependientes. Consultar `references/gate-checklist.md`.

## Restricciones
- No inventar actores, objetivos, KPI, reglas, estados, relaciones, dependencias ni criterios de aceptación.
- Diferenciar hechos, inferencias, supuestos, hipótesis, vacíos y decisiones humanas; preservar fuentes contradictorias.
- Markdown OKF v0.2 con STD-OKF-001 vigente; `status: draft`; no asignar `verified` ni `stable` sin autorización.
- No crear commits, MR ni publicar la KB sin autorización explícita.
- Si falta un input requerido, registrar el bloqueo y una pregunta; no fabricar evidencia.

## Contrato de conformidad documental
- Antes de entregar Markdown conceptual, ejecutar `python scripts/validate.py <archivo.md>` (usa `scripts/validate_okf.py` de la raíz del plugin).
- La validación no equivale a aprobación humana ni a publicación. Con STD-OKF-001 v0.1.0-stable, `TRM BCP BO STK BCAP BR IMD` son tipos aprobados; en `--publication` se rechazan los tipos no registrados en el catálogo.
- Para JSON/YAML operativos en `comsatel/` usar contratos operativos; no forzar frontmatter OKF.

## Mapeo obligatorio de rutas
Leer `assets/pathmap.md` de la raíz del plugin. Antes de producir archivos, recibir del orchestrator `workspace_root`, `document_type`, `output_dir`, `pathmap_version`, `run_id` y `override`. Verificar `type` e `id` del frontmatter contra el contrato y guardar en el destino resuelto con `scripts/validate_pathmap.py`. Reportar rutas reales en el manifiesto de salida; detenerse ante tipo desconocido, ruta divergente o falta de contrato.
