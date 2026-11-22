# Perfil OKF v0.2 + STD-OKF-001 v0.1.0-stable

Tipo principal para este skill: `RCP` (tipo aprobado en baseline v1.2.0).

Usar `templates/deliverable.md` como punto de partida y sustituir TODOS los placeholders con valores verificados antes de ejecutar el validador. No fabricar fuentes, fechas ni aprobaciones. Si no hay evidencia suficiente, detener publicación y registrar el bloqueo en `.comsatel/requirements-engineering/runs/<run-id>/`.

Campos obligatorios: `type,id,title,description,version,status,owner,classification,tags,generated.by,generated.at,sources`. `version` debe ser SemVer entre comillas, `generated.at` ISO 8601 con zona, `tags` minúsculas sin duplicados. `sources[].resource` es obligatorio. `pack` y `skill` son obligatorios en entregables del pack.

Los `type` UXR/FLW/SCR/CMP/TKN/WEB/MOB/HOF están aprobados en STD-OKF-001 v0.1.0-stable.

No usar `artifact_type`, `source_refs`, `reviewed_by` ni `lifecycle_status` como alias. `verified` solo si existe verificación real. `status: stable` requiere gobierno externo, no lo asigna el validador.

Validador común: `python scripts/validate_okf.py <documento.md>` desde raíz del plugin; publicación estricta `--publication`.
