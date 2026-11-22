# Ejemplo de biz-pack-validator-publisher

Entrada: Todos los entregables de G1 a G5 en `business/` y sus gates aprobados.
Salida esperada: actualiza el BCP tipado en `business/context-packs/` con inventario, trazabilidad, huecos, consumidores y readiness; devuelve los resultados de gate estructurados al orchestrator, que es el único que persiste el gate-report.
Bloqueo de ejemplo: afirmación sin fuente => registrar pregunta abierta con responsable y marcar CONDITIONAL o NOT_READY; no inventar contenido.
