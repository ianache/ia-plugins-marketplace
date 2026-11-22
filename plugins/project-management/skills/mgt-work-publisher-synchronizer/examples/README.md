# Ejemplo de mgt-work-publisher-synchronizer

Entrada: `SSP` con gate G2 aprobado, User Stories OKF aprobadas, configuración de producto-proyecto de GitLab y `GITLAB_PAT` en el entorno (solo se verifica que exista; nunca se imprime ni se guarda).
Salida esperada: resultado estructurado de publicación devuelto al orchestrator en `.comsatel/project-management/runs/<run-id>/`.
Bloqueo de ejemplo: fecha, costo o capacidad sin fuente => registrar pregunta abierta con responsable y marcar CONDITIONAL o NOT_READY; no inventar el dato.
