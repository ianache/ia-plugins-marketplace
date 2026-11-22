# STD-WORKFLOW-001 — Modos de ejecución

Los modos describen el **escenario** y no la operación documental:
- `GREENFIELD`: diseño de solución nueva sin implementación previa que preservar.
- `BROWNFIELD`: reconstrucción/regularización desde implementación existente, incluso si el documento no existe.
- `EVOLUTION`: cambio controlado respecto de baseline existente; admite `NO_CHANGE`.

`artifact_action` es independiente: `CREATE`, `UPDATE`, `NO_CHANGE`, `BLOCKED`. `BROWNFIELD + CREATE` es válido. No clasificar GREENFIELD por ausencia de archivo.

Cada pack declara `execution_modes` soportados. El orquestador selecciona modo, registra justificación, snapshot/baseline y DAG específico; especialistas no cambian modo ni estados oficiales. Cambios de dependencias disparan impacto selectivo y reevaluación de gates. Las autorizaciones `DEVELOPMENT_READY` pertenecen al orquestador de handoff, no a un especialista. No inferir aprobación por `status: stable`.
