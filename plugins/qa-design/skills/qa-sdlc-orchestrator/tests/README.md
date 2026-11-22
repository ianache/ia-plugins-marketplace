# Pruebas

`python -m unittest discover -s tests` desde la carpeta del skill (Python 3 y PyYAML). `test_skill_contract.py` valida estructura, metadatos, plantillas OKF y gates. `test_orchestrator.py` cubre las pruebas negativas obligatorias del orquestador (G0 bloqueado, dependencia sin gate PASS, evidencia ausente, doble despacho, cambio de estado por un especialista, ciclo de DAG, intervención humana sin reevaluación).
