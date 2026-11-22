# Perfil OKF v0.2 + STD-OKF-001 v1.9.0-stable

El orchestrator no produce documentos conceptuales: sus artefactos (`execution-plan.json`, `task-ledger.json`, `gate-register.json`) son operativos y viven en `.comsatel/business-knowledge/runs/<run-id>/`. Exige que los skills entreguen Markdown OKF con `type` en {TRM, BCP, BO, STK, BCAP, BR, IMD}, `status: draft`, `product`, `pack: business-knowledge` y `skill`. Estos tipos están aprobados en v1.9.0-stable (`BR` desde v1.2.0).
