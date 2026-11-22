# Política de rutas de salida

El único origen del mapeo es `assets/pathmap.md` de la raíz del plugin. Los entregables `BSN` viven en `business/scenarios/`, nunca en `comsatel/`, `design/` ni `requirements/`. El orchestrator guarda solo sus artefactos de control en `.comsatel/business-knowledge/runs/<run-id>/`. Un tipo sin mapeo queda bloqueado; solo una ruta explícita del usuario puede cambiar el destino, con registro de excepción. La ruta de un documento y la validez de su tipo OKF son controles distintos.
