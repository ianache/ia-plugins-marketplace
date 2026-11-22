# Validación de rutas v1.0.0 (pathmap_version 1.5.0)

Ejecutar `python -m unittest discover -s tests -p test_pathmap.py -v`. El script `scripts/validate_pathmap.py` verifica existencia, ruta y `type` del frontmatter, pero **no** valida todo el perfil STD-OKF-001 ni autentica aprobaciones. Los tipos distintos de RCP y US deben homologarse antes de automatizar su ruta por defecto.
