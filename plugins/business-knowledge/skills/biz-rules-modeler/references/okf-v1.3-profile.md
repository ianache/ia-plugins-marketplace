# Perfil OKF v0.2 + STD-OKF-001 v0.1.0-stable

Tipos de este skill: BR. `TRM BCP BO STK BCAP BR IMD` son tipos **aprobados** en v0.1.0-stable.

Usar las plantillas de `templates/` como punto de partida y sustituir TODOS los placeholders con valores verificados antes de ejecutar el validador. No fabricar fuentes, fechas ni aprobaciones. Si no hay evidencia suficiente, detener la publicación y registrar el bloqueo en `.comsatel/business-knowledge/runs/<run-id>/`.

Campos obligatorios: `type,id,title,description,version,status,owner,classification,tags,generated.by,generated.at,sources`; además `product`, `pack` y `skill` en los entregables del pack. `version` SemVer entre comillas, `generated.at` ISO 8601 con zona, `tags` en minúsculas sin duplicados, `sources[].resource` obligatorio y resoluble.

No usar `artifact_type`, `source_refs`, `reviewed_by` ni `lifecycle_status` como alias. `verified` solo si existe verificación real; `status: stable` requiere gobierno externo.

Validador: `python scripts/validate.py <documento.md>`; publicación estricta con `--publication`.

Fuentes: `sources` es una lista de objetos con `id` y `resource`. Una fuente eliminada se cita como referencia de git (`git:<commit>^:<ruta>`), no se deja sin `resource`.
