# Política de rutas de salida

El único origen del mapeo es `assets/pathmap.md` de la raíz del plugin. Los seis skills especializados reciben del orchestrator un contrato de rutas que deben cumplir. Los entregables viven en `management/<subcarpeta>/`; nunca en `.comsatel/`, `design/` ni `requirements/`. El orchestrator guarda solo sus artefactos de control en `.comsatel/project-management/runs/<run-id>/`. Tipos sin mapeo quedan bloqueados; únicamente una ruta explícita del usuario puede cambiar el destino, con registro de excepción.
