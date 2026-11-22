---
name: microservice-boundary-architecture-designer
description: Diseña límites de servicios y arquitectura hexagonal To-Be a partir de DDD, ADR y evidencia As-Is; sirve Greenfield y Evolution.
---
# Microservice Boundary & Architecture Designer

- Entradas: BC, CTX, AGG, VO, EVT, DSP/SSP, ADR, ASR, repositorios y As-Is cuando aplique.
- Para cada servicio: responsabilidades, ownership, inbound adapters, application services, dominio, outbound ports/adapters, dependencias, C4 y NFR. Un BC no equivale obligatoriamente a un microservicio.
- No redefinir el DDD aprobado. Reportar divergencias y decisiones pendientes.
- Salidas: `service-boundaries.md` y `service-architecture.md` en `design/microservices/<servicio>/`; además `c4-architecture.md` (tipo `C4`) en `codebase/<servicio>/docs/`.
- Aplicar STD-OKF-001 v1.11.0-stable; referenciar ADR y fuentes verificadas.


## Output Pathmap obligatorio
- Leer el contrato de ejecución recibido del orchestrator. No elegir el directorio por cuenta propia.
- Usar `assets/pathmap.md` y `assets/pathmap.json` (raíz del plugin); validar con `scripts/validate_pathmap.py`.
- Escribir entregables especializados en la ruta asignada por el pathmap (`design/` o `codebase/<servicio>/`); reportar `document_type`, `output_path`, `pathmap_version` y evidencia de validación.
- Una ruta diferente solo procede por instrucción explícita del usuario y debe quedar registrada en el ledger.
- El orchestrator mantiene planes, gates y ledger bajo `.comsatel/microservice-api-design/runs/<run-id>/`.
- Los Markdown generados requieren frontmatter conforme a `STD-OKF-001 v1.11.0-stable`, sin inventar tipos documentales aprobados.
