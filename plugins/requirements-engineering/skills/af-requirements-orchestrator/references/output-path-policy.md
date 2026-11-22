# Política de rutas de salida

El único origen del mapeo es `assets/pathmap.md`. Los cinco skills especializados reciben del orchestrator un contrato de rutas que deben cumplir. No guardar entregables en `design/requirements/` ni `requirements/<run-id>/` ni en `.comsatel/`. El orchestrator guarda solo sus artefactos de control en `.comsatel/requirements-engineering/runs/<run-id>/`. Tipos sin mapeo quedan bloqueados; únicamente una ruta explícita del usuario puede cambiar el destino, con registro de excepción. La ruta de un documento y la validez de su tipo OKF son controles distintos.

Ver tabla y contrato completo en `assets/pathmap.md` de la raíz del plugin.
