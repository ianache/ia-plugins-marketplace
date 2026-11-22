# Ejemplo architecture-conformance-assessor

1. Leer una entrada real y citar su ruta/versión.
2. Producir documento según `templates/okf-artifact.md` con campos reales.
3. Ejecutar `python scripts/validate.py architecture/<artifact>.md`.
4. Adjuntar `output-manifest.json` y solicitar aprobación G4.
