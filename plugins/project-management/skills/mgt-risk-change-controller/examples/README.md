# Ejemplo de mgt-risk-change-controller

Entrada: Plan e iteraciones aprobados (G1 a G3), riesgos de negocio (`BRISK` en el `BCP`), ASR/ADR de arquitectura, análisis de impacto (`IMP`), decisión de calidad (`QDC`) cuando exista, y el estado real del trabajo.
Salida esperada: RSK; CHG. `management/risks/RSK-NNN-<slug>.md` (un registro por iniciativa) y `management/changes/CHG-NNN-<slug>.md` (uno por solicitud).
Bloqueo de ejemplo: fecha, costo o capacidad sin fuente => registrar pregunta abierta con responsable y marcar CONDITIONAL o NOT_READY; no inventar el dato.
