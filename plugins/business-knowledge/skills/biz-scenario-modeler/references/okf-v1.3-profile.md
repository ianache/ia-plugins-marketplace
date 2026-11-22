# Perfil OKF v0.2 + STD-OKF-001 v1.9.0-stable

Tipos de este skill: BSN. `TRM BCP BO STK BCAP BR IMD BSN` son tipos **aprobados** en v1.9.0-stable.

Usar `templates/scenario.md` como punto de partida y sustituir TODOS los placeholders con valores verificados antes de ejecutar el validador. No fabricar fuentes, fechas, reglas ni aprobaciones. Si no hay evidencia suficiente, registrar el bloqueo en `.comsatel/business-knowledge/runs/<run-id>/`.

Campos obligatorios: `type,id,title,description,version,status,owner,classification,tags,generated.by,generated.at,sources`; además `product`, `pack` y `skill`. `id` tiene la forma `BSN-NNN`; el nombre del archivo empieza por ese `id`.

Validadores: `python scripts/validate.py <documento.md>` (frontmatter OKF) y `python scripts/check_scenario.py <documento.md> --workspace <raíz>` (contrato de contenido). Publicación estricta con `--publication`.
