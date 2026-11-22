# Migración y cobertura documental

1. Inventariar todos los Markdown conceptuales generados por el pack y detectar frontmatter faltante o alias históricos.
2. Aplicar `templates/deliverable.md` del skill productor; preservar cuerpo, IDs y fuentes verificadas.
3. No convertir automáticamente `sources: []` en fuentes inventadas. Documentar originalidad cuando corresponda.
4. Ejecutar validador común; registrar errores y bloquear gate G6 ante no conformidad.
5. Revisar trazabilidad, gate y publicación por humano autorizado; solo entonces Merge Request.

**Alcance:** verificación de metadatos y tipos; no demuestra calidad semántica, cumplimiento total de enlaces OKF ni aprobación de gates.
