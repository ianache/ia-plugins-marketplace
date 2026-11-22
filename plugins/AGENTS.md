# Reglas para Agentes: Estándar STD-OKF-001 en `plugins/`

Este directorio contiene los plugins del catálogo. El estándar **STD-OKF-001** (OKF) tiene un único archivo maestro y varias copias distribuidas dentro de los plugins.

Antes de crear o modificar un plugin o skill, lee [GUIA-BUENAS-PRACTICAS.md](GUIA-BUENAS-PRACTICAS.md) (estructura, nombres, gates, HIL, portabilidad, pruebas y lista de verificación).

## Fuente de verdad

- **Maestro:** `plugins/STD-OKF-001-v*.md` (hoy `STD-OKF-001-v1.9.0-stable.md`).
- **Sincronización:** `python plugins/scripts/sync_std.py --check` informa las copias, las listas de tipos de los validadores y las referencias a versiones anteriores; `--apply` las propaga desde el maestro. La prueba `plugins/scripts/test_sync_std.py` falla si hay discrepancias.
- Cualquier cambio al estándar se hace **primero** en el maestro. Las copias dentro de los plugins nunca se editan directamente.

## Copias distribuidas (destinos de propagación)

| Plugin | Ubicación de la copia |
| :--- | :--- |
| architecture-design, business-knowledge, data-modeling-database-design, ddd-domain-design, microservice-api-design, mobile-application-design, requirements-engineering, solution-ideation, ux-ui-design, web-platform-design | `<plugin>/standards/STD-OKF-001-v*.md` |
| qa-design | `qa-design/skills/<skill>/resources/STD-OKF-001.md` (una copia por skill: qa-sdlc-orchestrator, qa-feature-analyzer, qa-quality-intelligence, qa-agentic-test-reviewer, qa-agentic-test-engineer, qa-test-design, qa-test-design-reviewer) |

Descubre destinos siempre con búsqueda (`**/STD-OKF-001*`) en vez de confiar solo en esta tabla; si aparece un plugin nuevo, inclúyelo.

## Flujo obligatorio ante un cambio al estándar

1. **Reflejar en el maestro.** Si el cambio llegó a otra copia o a un archivo `STD-OKF-001-*.md` cualquiera, trasládalo al maestro `plugins/STD-OKF-001-v*.md` y deja ese archivo como versión vigente. Si cambia la versión, renombra el maestro (`v<nueva>`) y actualiza las referencias al nombre anterior.
2. **Analizar impacto** en cada plugin destino, **antes** de copiar nada:
   - Diff entre el maestro y cada copia (`diff` / hash).
   - Buscar en los `SKILL.md`, contratos (`contracts/`), plantillas (`templates/`, `assets/`), validadores (`scripts/validate.py`), pruebas (`tests/`) y referencias del plugin los elementos que dependen de lo cambiado (campos de frontmatter, tipos, estados, gates, reglas de nomenclatura, versión citada del estándar).
   - Clasificar por plugin: `SIN_IMPACTO`, `SOLO_COPIA` (basta reemplazar el archivo), `REQUIERE_AJUSTE` (hay que modificar skills, validadores o tests) o `ROMPE_COMPATIBILIDAD`.
3. **Presentar el informe de impacto al humano (HIL)** con: resumen del cambio, tabla plugin → clasificación → archivos afectados → ajustes propuestos, y riesgos.
4. **Esperar aprobación explícita** por plugin (o global). **No propagar sin ella.** Una aprobación aplica solo a los plugins y al cambio indicados, no a cambios posteriores.
5. **Propagar solo a los plugins aprobados:** copiar el maestro a cada destino (respetando el nombre de archivo propio de cada ubicación), aplicar los ajustes aprobados y ejecutar las pruebas/validadores de cada plugin afectado.
6. **Verificar y reportar:** comprobar que las copias aprobadas tienen hash idéntico al maestro, y listar los plugins pendientes o rechazados (quedan desincronizados de forma consciente y deben declararse como tal).

## Verificación de sincronía

```sh
cd plugins
md5sum STD-OKF-001-v*.md */standards/STD-OKF-001*.md */skills/*/resources/STD-OKF-001*.md | sort
```

Los hashes distintos al del maestro indican copias desactualizadas. Informarlo siempre al humano; no corregirlo sin aprobación.

## Estado conocido

- Las copias de `qa-design` se alinearon con el maestro v1.3.0-stable (`96134047…`) tras analizar su impacto: sus tests pasan y los tipos QA ya constan como aprobados.

## Versionado SemVer de plugins y skills (trazabilidad)

Todo cambio a un plugin o a sus skills **debe** subir la versión según [SemVer 2.0.0](https://semver.org/lang/es/) (`MAJOR.MINOR.PATCH`) en el mismo commit que el cambio. No se publica ni se propaga contenido modificado con la versión anterior.

### Dónde vive la versión

| Elemento | Ubicación | Estado actual |
| :--- | :--- | :--- |
| Plugin | `<plugin>/.claude-plugin/plugin.json` → `"version"` | Existe en los 11 plugins. |
| Skill | `SKILL.md` → frontmatter `metadata.version` | Solo `qa-design` lo usa hoy; en los demás plugins la versión del skill se rige por la del plugin. No añadir `metadata.version` a otros plugins sin aprobación. |
| Estándar OKF | Nombre del maestro `STD-OKF-001-v<ver>.md` | Ver flujo de propagación arriba. |

### Línea base 1.0.0 (2026-10-29)

El **2026-10-29** todos los plugins se reiniciaron a **1.0.0**, que es la **línea base absoluta** del catálogo. Las versiones anteriores de los `CHANGELOG.md` están marcadas «(pre-línea base)» y son solo historial. Esta es la única excepción a la regla de no retroceder la versión; no se repite sin decisión explícita del responsable.

- **Línea vigente (autorizada por el responsable el 2026-11-07):** la línea base de 1.0.0 no se mantuvo en el repo. Desde esa fecha la versión vigente de cada plugin es la de su `plugin.json` (p. ej. `1.2.x`, `2.0.0`), y cada cambio sube SemVer desde ahí según las reglas de incremento. No se retrocede ninguna versión.
- Los cambios que aún no tengan versión asignada se registran en `[Sin publicar]` del `CHANGELOG.md` hasta que se decida su número.
- Los artefactos generados con versiones anteriores (ZIP en `dist/`, `.pptx` y `.pdf` de `plugins/`) se regeneran en el reempaquetado.

### Reglas de incremento

- **PATCH** (`x.y.Z`): correcciones sin cambio de contrato: erratas, aclaraciones, bugs en scripts/validadores, ajustes de pruebas o documentación.
- **MINOR** (`x.Y.0`): funcionalidad nueva compatible: skill nuevo, sección/campo opcional, nueva plantilla, resincronizar una copia del estándar sin cambios de contrato. Reinicia PATCH a 0.
- **MAJOR** (`X.0.0`): cambio incompatible: eliminar o renombrar un skill, cambiar entradas/salidas, `type` o rutas de salida, endurecer un gate, o propagar una versión del estándar clasificada `ROMPE_COMPATIBILIDAD`. Reinicia MINOR y PATCH a 0.
- Plugins en `0.y.z` (inicial): los cambios incompatibles suben MINOR; igualmente documentarlos como incompatibles.
- Pre-releases con sufijo (`-draft`, `-rc.1`) solo si el humano lo indica.

### Propagación entre plugin y skills

- Si cambia un skill, sube la versión del skill (cuando la lleve) **y** la del plugin que lo contiene, con al menos el mismo nivel de incremento.
- Si cambia un plugin sin tocar skills (README, scripts, copia del estándar), sube solo la del plugin.
- Propagar `STD-OKF-001` a un plugin cuenta como cambio de ese plugin: sube su versión (MINOR por defecto; PATCH si solo es copia idéntica de una corrección menor; MAJOR si rompe compatibilidad).

### Procedimiento

1. Determinar el nivel de incremento y justificarlo en el informe de impacto (para cambios al estándar, junto con la aprobación HIL del paso 4). Si hay duda entre dos niveles, proponer el mayor y preguntar al humano.
2. Actualizar `plugin.json` / `metadata.version` y mantener consistentes README, `DOCUMENTACION.md` u otros textos que citen la versión (buscar el número anterior).
3. Registrar el cambio en `<plugin>/CHANGELOG.md` (Keep a Changelog: Añadido / Cambiado / Corregido / Eliminado), moviendo lo de `[Sin publicar]` a la nueva versión con fecha. Citar la versión también en el mensaje de commit (`feat(<plugin>): ... [vX.Y.Z]`). Si el plugin aún no tiene `CHANGELOG.md`, crearlo.
4. Verificar que ningún plugin modificado conserva su versión anterior (`git diff` sobre los manifiestos).

## Prohibiciones

- No editar copias de plugin sin pasar por el maestro.
- No propagar ni sobrescribir copias sin aprobación humana explícita.
- No modificar un plugin o skill sin subir su versión SemVer.
- No ocultar plugins desincronizados: deben figurar en el informe.
- Al hacer commit, seguir las reglas del `AGENTS.md` raíz (p. ej. actualizar `.agents/skills/README.md` si cambian skills).
