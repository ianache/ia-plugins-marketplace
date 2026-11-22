# Solicitud de control de cambios — tipo documental genérico de informe

- **Estado:** sin efecto para `domain-discovery.md`, que usa el tipo aprobado `ACP` (pathmap, `typed_outputs`; plantilla `templates/domain-discovery-acp.md`). Pendiente de cierre por gobernanza del estándar STD-OKF-001; no se aprobó un tipo nuevo.
- **Solicitante:** plugin `ddd-domain-design` v2.1.0.
- **Motivo:** el documento de descubrimiento de dominios (`domain-discovery.md`, salida de `ddd-domain-discovery`) es un informe de hechos, inferencias, supuestos y vacíos sobre un alcance. Hoy no tiene tipo OKF registrado. Los tipos más cercanos no encajan: `DSH` especifica pantallas e informes, `STR` es un informe de estado de periodo y `QAR` es un informe de calidad de KB.
- **Tipo solicitado:** un tipo genérico de informe de análisis, con alcance transversal a packs, para documentos que reportan hallazgos de análisis sin especificar pantallas ni estado de gestión.
- **Campos sugeridos:** `product`, `pack`, `skill`; `related` con enlaces Markdown; `sources` con `id`. Sin campos adicionales obligatorios.
- **Sigla:** la asigna gobernanza. Esta solicitud no propone una sigla registrada.
- **Uso provisional (superado):** `domain-discovery.md` ya no es auxiliar sin tipo: usa `ACP` con `templates/domain-discovery-acp.md`.
- **Alternativa si se rechaza:** integrar el descubrimiento como sección de un documento `BC` o `CTX` aprobado.
