# Validación v2.1.1

- Siete skills Claude con recursos propios y wrappers de validación.
- Perfiles y templates nuevos alineados al diccionario STD-OKF-001 v0.1.0-stable.
- Validador compartido comprueba YAML, campos, enums, SemVer, generated.at, sources, tipo, campos condicionales y cuerpo no vacío.
- El estándar v1.3.0 continúa draft; la publicación usa tipos aprobados en baseline v1.2.0.
- `us_ids.py` verifica el formato `RCP-NNN-US-NNN`, el nombre del archivo y los IDs duplicados entre archivos, KB (`--also`) y ramas (`--git-ref`); `validate_okf.py` rechaza IDs de US que no cumplan ese formato.
- Limitación: no verifica contenido semántico, validez de rutas ni autorización humana.
