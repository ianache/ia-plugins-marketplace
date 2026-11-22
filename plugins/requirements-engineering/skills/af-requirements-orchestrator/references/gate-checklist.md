# Gates

G0: alcance y fuentes autorizadas. G1: RCP trazable. G2: línea base de negocio disponible y aprobada (BR, IMD, TRM del plugin `business-knowledge`). G3: HU independientes con ID `RCP-NNN-US-NNN` único (`us_ids.py check` en 0 errores). Si hay épicas (`RCP-NNN-EPC-NNN`): cada `related` apunta a una HU existente, ninguna HU pertenece a dos épicas, la épica tiene criterio de agrupación explícito y sus criterios de aceptación se trazan a criterios de sus historias. G4: criterios testeables. G5: impacto clasificado. G6: handoff y trazabilidad.

No aprobar automáticamente ni inferir la identidad del revisor.

- Output routing: validar el contrato contra `assets/pathmap.md` y ejecutar `scripts/validate_pathmap.py`; tipo sin mapping o ruta divergente = BLOCKED.
