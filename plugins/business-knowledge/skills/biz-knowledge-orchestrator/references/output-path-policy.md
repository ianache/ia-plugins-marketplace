# Política de rutas de salida

Mapeo único en `assets/pathmap.md`. El orchestrator guarda solo sus artefactos de control en `.comsatel/business-knowledge/runs/<run-id>/`; los entregables van en `business/<subcarpeta>/`. Tipos sin mapeo quedan BLOCKED; solo una ruta explícita del usuario cambia el destino, con registro de excepción.
