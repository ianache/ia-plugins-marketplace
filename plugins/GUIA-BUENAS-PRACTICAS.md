# Guía de buenas prácticas para crear y evolucionar plugins y skills

Audiencia: colaboradores que crean o modifican plugins en `plugins/`. Complementa las reglas de gobierno de [AGENTS.md](AGENTS.md) (estándar OKF y SemVer) y no las reemplaza.

Origen: convenciones observadas en los 11 plugins actuales y reglas de empaquetado del skill `.agents/skills/anthropic-plugin-packager`. Cada regla se marca así:

- **OBLIGATORIO**: se cumple hoy en todos (o casi todos) los plugins, o lo exige el empaquetado Anthropic.
- **RECOMENDADO**: práctica de solo algunos plugins; adóptala en plugins nuevos salvo motivo justificado.

> Nota: la guía es una primera versión derivada de lectura de los archivos; los validadores y pruebas de los plugins no se ejecutaron al redactarla. Corrige la guía si una regla no coincide con la realidad.

---

## 1. Estructura

### 1.1 Plugin

```text
<plugin>/
├── .claude-plugin/plugin.json      # OBLIGATORIO (solo el manifiesto va aquí)
├── README.md                       # OBLIGATORIO
├── CHANGELOG.md                    # OBLIGATORIO (Keep a Changelog, sección [Sin publicar])
├── templates/                      # SOLO documentos OKF comunes a más de un skill (ver 1.2)
├── skills/<skill>/SKILL.md         # OBLIGATORIO
├── scripts/                        # workflow.py + validate_okf.py (+ validate_pathmap.py)
├── standards/STD-OKF-001-v*.md     # copia del estándar; ver AGENTS.md
├── tests/                          # pytest/unittest
├── assets/pathmap.md               # RECOMENDADO si el plugin genera documentos OKF
├── OUTPUT-PATH-POLICY.md           # RECOMENDADO (con pathmap)
├── VALIDATION.md / VALIDATION-PATHS.md   # RECOMENDADO: qué se valida y qué no
├── COVERAGE-MATRIX.md              # RECOMENDADO al consolidar/migrar skills
└── DOCUMENTACION.md                # RECOMENDADO en plugins grandes
```

- **OBLIGATORIO:** `skills/`, `agents/`, `commands/` y `hooks/` son hermanos de `.claude-plugin/`; nunca se colocan dentro de ella.
- **OBLIGATORIO:** preferir auto-discovery y un manifiesto mínimo.
- **OBLIGATORIO:** no versionar `__pycache__`, `.pytest_cache`, `.env`, secretos, tokens ni salidas temporales.

### 1.2 Skill

```text
skills/<skill>/
├── SKILL.md              # corto; delega el detalle
├── references/           # contract.md, gate-checklist.md, technical-guidance.md, okf-v1.3-profile.md, output-path-policy.md
├── templates/            # plantillas de los documentos OKF que produce ESTE skill
├── assets/  examples/    # README mínimo o ejemplo sintético
└── scripts/validate.py   # wrapper delgado sobre scripts/validate_okf.py del plugin
```

- **OBLIGATORIO:** un recurso privado de un skill vive dentro de su carpeta. Un recurso usado por varios skills se eleva a `scripts/` u otro directorio compartido del plugin solo si actualizas todas las referencias.
- **OBLIGATORIO:** `skills/<skill>/templates/` contiene las plantillas de los documentos que produce ese skill, y solo esas.
- **OBLIGATORIO:** `templates/` de la raíz del plugin contiene solo plantillas de documentos OKF comunes a más de un skill. Hoy no hay ninguna. Una plantilla de un único productor no va ahí, ni como copia en los skills.
- **OBLIGATORIO (registros operativos):** `gate-report.yaml`, `task-result.yaml`, `execution-plan.yaml`, `task-ledger.yaml` y `gate-register.yaml` viven en `skills/<orquestador>/templates/`, aunque los escriba un skill especialista. Son documentos de control del flujo del workflow y los mantiene el orquestador de cada plugin. Ningún otro skill ni la raíz del plugin guarda copias.
- **OBLIGATORIO (tipo documental):** toda plantilla de documento OKF (Markdown conceptual) declara un `type` definido en el `STD-OKF-001-v*-stable.md` vigente (hoy `v1.9.0-stable`; confirma la versión vigente del maestro en `plugins/`). El tipo va en el frontmatter. Antes de crear una plantilla, verifica la sigla en la tabla de tipos del estándar; si no existe, no la inventes ni uses alias. Un tipo nuevo exige cambiar el estándar con aprobación HIL.
- **Registros operativos (sin `type`):** los YAML de estado y control no son OKF y no llevan `type`. Así lo fija el estándar: las salidas del orquestador (planes, estado, contratos de ruta y registros de gate) son operativas. Son `execution-plan.yaml`, `task-ledger.yaml`, `gate-register.yaml`, `gate-report.yaml` y `task-result.yaml`. Los dos últimos los escriben los skills especialistas, pero sus plantillas viven en la carpeta del orquestador (ver 1.2). Se documentan en `DOCUMENTACION.md` como registros operativos.
- **OBLIGATORIO:** no dupliques lógica en los `validate.py` de los skills; importa la del plugin.
- **RECOMENDADO** (estilo `qa-design`): `contracts/*.schema.json` por skill, gates en YAML y checkers `check_*.py` con pruebas propias.

## 2. Nombres y manifiesto

- **OBLIGATORIO:** el skill va en kebab-case y el nombre de la carpeta es igual a `name` del frontmatter.
- **OBLIGATORIO:** prefijo que identifique al plugin: `af-` (requirements-engineering), `biz-` (business-knowledge), `architecture-`, `ddd-`, `microservice-`/`api-`, `qa-`, `ux-`/`ui-`, `mobile-`.
- **OBLIGATORIO:** exactamente un `*-orchestrator` por plugin.
- **OBLIGATORIO:** `plugin.json` con `name`, `version` (SemVer), `description` y `author.name`. Hoy el autor varía (`COMSATEL`, `COMSATEL Engineering`, `COMSATEL Architecture`) y `architecture-design` no lo tiene: unifica en el siguiente cambio.
- **RECOMENDADO:** `description` concisa que diga qué hace y cuántos skills incluye.

## 3. Escribir un SKILL.md

- **OBLIGATORIO:** frontmatter con `name` y `description` (una sola línea). Para decidir cuándo activarse, la descripción debe decir cuándo usar el skill y con qué palabras clave (p. ej. «Usar para TRM; glosario; siglas»).
- **OBLIGATORIO:** `SKILL.md` corto (hoy 20–62 líneas). El detalle va en `references/` (progressive disclosure) y el `SKILL.md` lista las rutas de esos recursos.
- **RECOMENDADO:** secciones fijas, como en RE y BK: `Activación`, `Entradas obligatorias`, `Procedimiento` (pasos numerados), `Salidas`, `Reglas`, `Gate Gn`, `Restricciones`.
- **RECOMENDADO:** redactar en español, como el resto del catálogo. `qa-design` usa secciones en inglés; no lo repliques en plugins nuevos.
- `metadata.version` en el frontmatter lo usa solo `qa-design`; no lo añadas en otros plugins sin aprobación (ver AGENTS.md).
- **OBLIGATORIO:** un skill nunca lanza otros skills ni edita el plan.

## 4. Orquestador, gates y control humano

- **OBLIGATORIO:** solo el orquestador planifica, despacha tareas y evalúa gates. Los especialistas no se autoaprueban, no editan el registro de gates y no invocan a otros skills.
- **OBLIGATORIO:** gates numerados `G0..Gn` y declarados con contrato (`references/contract.md`: Gate, Inputs, Precondición, Outputs, Postcondición, Readiness, Evidence, Bloqueo, Handoff).
- **OBLIGATORIO (fail-closed):** sin evidencia el resultado es `UNCERTAIN` o `FAIL`; no existe PASS parcial. Lo pendiente va a `deferred_items` con `decision_ref`.
- **OBLIGATORIO (HIL):** `READY`, `CONDITIONAL` y `NOT_READY` son resultados técnicos, no aprobación. Solo `approved: true` registrado por una persona autorizada habilita las tareas dependientes. El script de `workflow.py` no autentica identidad; no lo presentes como control de acceso.
- **OBLIGATORIO:** estado por defecto `status: draft`. Nunca asignes `verified` o `stable` sin autorización.
- **OBLIGATORIO:** no hacer commit, MR ni publicación sin autorización explícita.
- **OBLIGATORIO:** el estado operativo (plan, estado, gate-register) lo escribe solo el orquestador, en `.comsatel/<plugin>/runs/<run-id>/` (el valor exacto es `orchestrator_root` del pathmap de cada plugin).
- **Evidencia:** cada hecho lleva fuente, ubicación, fecha o versión, clasificación, confianza y owner. Separa hechos, inferencias, supuestos y vacíos. No inventes actores, reglas ni KPI.
- **RECOMENDADO** (modo `STRICT` del packager): ante un error estructural, dependencia ausente o ruta no portable, bloquear en vez de corregir en silencio. Si una corrección cambia la semántica de un skill, detenerse y pedir revisión humana.

## 5. Documentos OKF y rutas de salida

- **OBLIGATORIO:** todo documento generado cumple `STD-OKF-001` con el frontmatter de `templates/deliverable.md`: `type`, `id`, `title`, `description`, `version` (SemVer), `status`, `owner`, `classification`, `tags`, `product`, `pack`, `skill`, `generated.by`, `generated.at` (ISO-8601 con zona) y `sources[]`.
- **OBLIGATORIO (tipo documental):** el `type` de cada documento Markdown OKF y de su plantilla debe existir en la tabla de tipos del `STD-OKF-001-v*-stable.md` vigente. Un documento OKF sin tipo aprobado queda `BLOCKED` para publicación. Los registros operativos YAML quedan fuera de esta regla (ver sección 1.2).
- `index.md` y `log.md` son archivos reservados y no llevan la plantilla general.
- **OBLIGATORIO (plugins con pathmap):** la ruta de salida se resuelve por `type` en `assets/pathmap.md`, no por el nombre del skill. Un `type` sin mapeo queda en `BLOCKED`. Solo una instrucción explícita del usuario cambia la ruta, y se registra la excepción.
- **OBLIGATORIO:** no escribas documentos especializados en `comsatel/`; esa carpeta es solo para estado de ejecución.
- Los tipos del catálogo v1.8.0-stable están aprobados; `--publication` rechaza solo los tipos no registrados.
- Cambiar el estándar: seguir el flujo del maestro y HIL de [AGENTS.md](AGENTS.md); nunca editar las copias.

## 6. Portabilidad (reglas del packager)

- **OBLIGATORIO:** sin rutas absolutas de usuario (`C:\…`, `/home/…`) ni traversal fuera del plugin (`../..` hacia afuera).
- **OBLIGATORIO:** las rutas de runtime compartidas usan `${CLAUDE_PLUGIN_ROOT}`.
- **OBLIGATORIO:** sin secretos empaquetados; no resolver `GITLAB_PAT` ni otros secretos durante el empaquetado.
- **OBLIGATORIO:** toda referencia de un `SKILL.md` a un archivo debe existir. Evita referencias colgantes tras borrar recursos.
- Orden de gates del packager (todos bloqueantes): descubrimiento de skills → validación de skills → dependencias → estructura del plugin → portabilidad → paquete.
- El ZIP distribuible tiene un único directorio raíz con el nombre del plugin y `plugin-package-manifest.json` con hashes SHA-256.

## 7. Validación y pruebas

- **OBLIGATORIO:** todo plugin tiene `tests/` y un validador ejecutable desde su raíz (`scripts/validate_okf.py`, o los `check_*.py` de QA).
- **RECOMENDADO:** `VALIDATION.md` que declare los límites. Hoy los validadores comprueban YAML, campos, enums, SemVer, `generated.at`, `sources` y tipo; no comprueban contenido semántico ni autorización humana.
- **RECOMENDADO:** `scripts/validate_pathmap.py` y `VALIDATION-PATHS.md` cuando hay pathmap.
- **RECOMENDADO:** `COVERAGE-MATRIX.md` al fusionar o migrar skills. Consolidar no equivale a funcionalidad validada.
- **OBLIGATORIO:** antes de cada cambio, ejecuta las pruebas y el validador del plugin y pega el resultado en la descripción del cambio. Los tests de humo (p. ej. UX, Mobile) son insuficientes cuando cambias lógica de gates o validadores: amplíalos.
- Los checks de revisión independiente los hace alguien distinto del autor.

## 8. Versionado, changelog y commits

- Reglas SemVer, propagación plugin↔skill y procedimiento: sección «Versionado SemVer» de [AGENTS.md](AGENTS.md).
- **OBLIGATORIO:** mantener consistente la versión en `plugin.json`, README y `DOCUMENTACION.md`. Evita desfases como el de `qa-design` (plugin 5.2.1, skill 5.2.0).
- **OBLIGATORIO:** `CHANGELOG.md` con Keep a Changelog. Los cambios nuevos entran primero en `[Sin publicar]`.
- **OBLIGATORIO:** commits Conventional Commits con alcance de plugin y versión: `feat(<plugin>): descripción [vX.Y.Z]`.
- **OBLIGATORIO:** si cambias skills de `.agents/skills/`, actualiza `.agents/skills/README.md` según el `AGENTS.md` de la raíz. Ese catálogo es distinto de `plugins/`.

## 9. Anti-patrones detectados (evitar)

| Anti-patrón | Dónde se vio | Qué hacer |
| :--- | :--- | :--- |
| Referencia a recursos retirados (`templates/legacy/`) | `requirements-engineering` (`MIGRATION-OKF.md`, dos `SKILL.md`, `technical-guidance.md`) | Eliminar o actualizar la referencia al retirar un recurso. |
| Documentación atrasada respecto a la versión | `requirements-engineering` (`VALIDATION.md` v1.1.0, `VALIDATION-PATHS.md` v1.2.0 frente al plugin 1.4.0) | Revisar documentos con versión citada en cada release. |
| Copia del estándar desactualizada | `qa-design` | Propagar con aprobación HIL. |
| Plantillas de un solo skill en la raíz del plugin, o copias de plantillas en varios skills | `ddd-domain-design` (`templates/` raíz con `task-result.yaml`, copias en cada skill); `qa-design` (`gate-report.yaml` copiado en 6 skills) | Plantilla OKF en `skills/<skill>/templates/`; registro operativo en la carpeta del orquestador; `templates/` de la raíz solo para documentos OKF comunes. |
| Registro operativo de control de flujo dentro de un skill especialista | `infra-architecture-design` (`task-result.yaml` en 5 skills), `uow-development-design` (`gate-report.yaml` en 6 skills), `business-knowledge` (`gate-report.md` en `biz-pack-validator-publisher`) | Mover la plantilla a la carpeta del orquestador del plugin. |
| Artefactos generados versionados | `__pycache__`, `.pytest_cache` en `plugins/` | Añadirlos al `.gitignore` y no commitearlos. |
| Skills generados por plantilla sin contenido propio | `ux-ui-design`, `mobile-application-design` (SKILL.md casi idénticos, tests mínimos) | Especializar `SKILL.md`, contratos y pruebas. |
| Idioma y estilo mezclados | `qa-design` (secciones en inglés, gates con nombre) | Alinear en plugins nuevos; migrar `qa-design` solo con decisión explícita. |
| Acoplamiento entre plugins | RE depende de que `business-knowledge` produzca G2 | Referenciar por IDs y contrato; documentarlo en `contract.md`. |

## 10. Lista de verificación antes de abrir un cambio

1. ¿La estructura cumple la sección 1 y los nombres la sección 2?
2. ¿Cada `SKILL.md` es corto, con descripción de activación y referencias existentes?
3. ¿Hay orquestador único, contratos y gates con HIL, y los especialistas no se autoaprueban?
4. ¿Los documentos generados usan el frontmatter OKF y la ruta resuelta por el pathmap?
5. ¿Sin rutas absolutas, secretos ni artefactos temporales?
6. ¿Pruebas y validador del plugin en verde, con evidencia?
7. ¿Versión SemVer subida en `plugin.json` (y skill si aplica) y coherente en README/DOCUMENTACION?
8. ¿`CHANGELOG.md` actualizado y commit `feat(<plugin>): ... [vX.Y.Z]`?
9. Si tocaste el estándar: ¿maestro actualizado, impacto analizado y aprobación HIL por plugin?
10. ¿Cada plantilla OKF vive en `skills/<skill>/templates/` (o en `templates/` del plugin si es común a varios skills), y los registros operativos YAML en la carpeta del orquestador? Si es un documento Markdown OKF, ¿declara un `type` aprobado en el STD vigente? Los registros operativos YAML no llevan `type`.
