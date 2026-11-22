# Ejemplos

`BSN-001-alta-cliente-con-servicio.md` es un escenario ilustrativo con datos ficticios. Muestra el contrato de `templates/scenario.md` completo, con readiness CONDITIONAL y una pregunta abierta que bloquea.

Verificación:
- `python scripts/validate.py examples/BSN-001-alta-cliente-con-servicio.md`
- `python scripts/check_scenario.py examples/BSN-001-alta-cliente-con-servicio.md` (sin `--workspace`: las reglas BR citadas no se verifican en este ejemplo).
