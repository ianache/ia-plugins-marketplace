# Contrato — architecture-context-and-evidence-designer

**Inputs:** lista de artefactos identificados con ID, versión, ruta, status, source hash opcional y gate anterior.

**Outputs:** documentos OKF v0.2 y `output-manifest.json`. Campos del manifest: `producer`, `inputs[]`, `outputs[]`, `sources[]`, `open_questions[]`, `gate`, `status`.

**Invariantes:** `generated.by` identifica skill/versión, `generated.at` refleja generación real; `sources` refleja procedencia comprobable; `verified` solo si existe verificación real. No fabricar evidencia.

**Gate:** G1, requiere decisión humana fuera del validador.

## Política de rutas
Consultar `assets/pathmap.md` de la raíz del plugin: entregables especializados en `./architecture/` (ADR `adrs/`, ASR `asrs/`); solo el orchestrator escribe control en `.comsatel/architecture-design/runs/<run-id>/`. Overrides únicamente por instrucción explícita.

## Enrutamiento obligatorio
Usar el contrato `document_type`/`output_dir` emitido por el orchestrator y el `assets/pathmap.md` de la raíz del plugin; bloquear rutas no mapeadas.
