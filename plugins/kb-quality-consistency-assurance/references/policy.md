# Política de ejecución y fuentes

- Google OKF v0.2: estructura y frontmatter mínimo; perfil COMSATEL `STD-OKF-001` agrega requisitos corporativos por versión.
- `index.md` y `log.md` son reservados y se validan por reglas propias; no aplicar plantilla general.
- `kb-comsatel` y `kb-okf-services` son PoC: adaptadores opcionales, sin dependencia rígida ni suposición de coexistencia en producción.
- Snapshot de Git por commit SHA es fuente autoritativa; índices y vistas MCP/WebDAV se comprueban contra su generación y política de publicación.
- Verificar consistencia temporal de indexación, publicación de documentos `stable` y Context Packs, según reglas de estado del perfil efectivo.
- `audit`: solo lectura. `change-review`: compara baseline y candidate. `remediation`: prepara parches/MR para revisión, sin publicación automática.
- Nunca exponer secretos ni descargar conocimiento fuera de permisos autorizados.
