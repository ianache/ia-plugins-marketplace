# Scripts del orquestador

- `uow_orchestrator.py`: controlador fail-closed (`init`, `g0`, `expand`, `authorize`, `start`, `complete`, `gate`, `human`, `reopen`, `invalidate`, `cancel`, `waive`, `status`, `eligible`, `verify-authorization`).
- `gate_governance.py`: decisión determinista de gates (`AUTO`, `CONDITIONAL_HIL`, `MANDATORY_HIL`).
- `uow_package.py build`: genera `uow-package.yaml` con el digest del paquete.
- `check_uow_package.py`: checks `script` de cada gate.
