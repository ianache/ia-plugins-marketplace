# Migración de documentos de reglas heredados

Aplica a catálogos de reglas creados antes del perfil del plugin (frontmatter sin `type` registrado, `status` o `classification` fuera de enum, `generated` como texto, `sources` sin `resource`). Migrar sin cambiar el contenido de las reglas; cualquier cambio de enunciado requiere revisión humana.

## Lista de comprobación

1. **Tipo.** `type` debe ser un tipo registrado. Un catálogo de reglas es `CTLG` con `indexes: BR`; no usar `BRC`, `business-rules-catalog` ni similares.
2. **Identificador.** `id` coincide con el prefijo del nombre del archivo. Un catálogo narrativo usa `CTLG-<NOMBRE>`.
3. **Campos obligatorios.** `title`, `description`, `version` (SemVer entre comillas), `status` (`draft`, `stable` o `deprecated`), `owner`, `classification` (`public`, `internal`, `confidential` o `restricted`), `tags` (minúsculas, sin duplicados), `product`, `pack` y `skill` si el documento pertenece al pack.
4. **Procedencia.** `generated` es un mapa con `by` (productor y versión, o `human:`/`process:`) y `at` (ISO 8601 con zona).
5. **Fuentes.** `sources` es una lista de objetos con `id` y `resource`. Una fuente eliminada se cita como `git:<commit>^:<ruta>`.
6. **Reglas.** Cada regla del catálogo tiene su archivo `BR-NNN.md`. Antes de crear uno, buscar en el workspace una regla con el mismo enunciado y reutilizar su ID. Los IDs locales del documento fuente se convierten a los IDs del workspace, y las referencias cruzadas del texto se actualizan con el mismo mapa.
7. **Campos propios.** Campos como `readiness`, `owners` o `derived_from` pueden conservarse; el validador los ignora. No sustituir campos obligatorios por ellos.
8. **Validación.** `python scripts/validate.py <documento.md>` para cada documento; `python scripts/validate_pathmap.py --workspace <raíz> --file <ruta> --type CTLG` para el catálogo; `python scripts/rules.py check <dir>` para las reglas.
9. **Registro.** Dejar en el documento una nota de migración con la fecha, el mapa de IDs usado y la lista de campos cambiados.
