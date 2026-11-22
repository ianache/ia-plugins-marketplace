# Contrato biz-pack-validator-publisher

- Gate de cierre: G6 (gate de entrada: G5)
- Inputs: Todos los entregables de G1 a G5 en `business/` y sus gates aprobados.
- Precondición: insumos autorizados, con versión y provenance; gate previo aprobado.
- Outputs: actualiza el BCP tipado en `business/context-packs/` con inventario, trazabilidad, huecos, consumidores y readiness; devuelve los resultados de gate estructurados al orchestrator, que es el único que persiste el gate-report.
- Postcondición: entregables con origen, preguntas abiertas y owners.
- Readiness: READY / CONDITIONAL / NOT_READY.
- Evidence: fuente, ubicación, fecha o versión, clasificación, confianza, owner.
- Bloqueo: fuente faltante, contradicción crítica, decisión de negocio pendiente o gate previo no aprobado.
- Handoff: IDs de artefactos, rutas, versión, dependencias, preguntas y estado del gate.
- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
