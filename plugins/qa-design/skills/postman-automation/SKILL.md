---
name: postman-automation
description: Usar cuando los casos de prueba aprobados de un microservicio API deban consolidarse en una colección Postman organizada por funcionalidad (endpoint) y por caso de prueba, con los criterios de aceptación en la documentación de cada request.
metadata:
  version: "1.0.0"
  author: "COMSATEL"
  type: "qa"
---
# Postman Automation

## Propósito
Consolidar, para **un microservicio API**, los TC aprobados que prueban sus funcionalidades y convertirlos en una colección Postman (`test/functional/postman.json`) con esta estructura:

- Carpeta de primer nivel por funcionalidad: `RF##-<nombre de la funcionalidad del endpoint>`.
- Dentro, una carpeta por caso de prueba: `<ID del TC> - <Nombre del TC>`.
- Dentro, los requests del caso.

La trazabilidad (AC, historia, TSN) va en la **descripción de la carpeta**, nunca en su título. Cada request documenta en `request.description` su objetivo y **todos** los criterios de aceptación de su caso, copiados literalmente de la fuente.

No genera el harness de CI ni ejecuta pruebas por sí mismo: eso corresponde a `qa-agentic-test-engineer` y al pipeline del microservicio.

## Activación y alcance
Usar cuando:
- existe un `QTD` con TC `READY` para un microservicio que expone API HTTP (contrato OpenAPI disponible);
- se pide consolidar o actualizar la colección Postman funcional de ese microservicio.

Exclusiones:
- Superficies WEB, MOBILE o CROSS_SURFACE: no son requests de API; se tratan con los skills de automatización de cada superficie.
- TC con `test_type: rendimiento`: los implementa `loadtest-automation`.
- Pruebas de integración Java (`*IT.java`), ArchUnit y pruebas de carga: fuera de alcance; el skill solo las **referencia** en la trazabilidad si ya cubren un AC.
- Microservicios sin API HTTP de negocio (solo eventos): declarar `NOT_APPLICABLE` y no generar colección de negocio.

Relación con otros skills: lo invoca `qa-sdlc-orchestrator` después de `qa-test-design-reviewer`, en paralelo con `qa-agentic-test-engineer` cuando ambos aplican. No reemplaza al `qa-agentic-test-reviewer`.

## Modos de operación
| Modo | Comportamiento |
|---|---|
| Greenfield | Crea la colección desde los TC aprobados y el contrato OpenAPI. Las comprobaciones de línea base se marcan `N/A` con justificación. |
| Brownfield | Inventaría la colección existente, asigna cada request a un TC o lo marca como `HUERFANO`, y reporta lo que no tiene TC. No da por buena una colección existente sin verificarla. |
| Evolution | Compara contra la colección de la línea base aprobada. Marca cada carpeta como `CREATE`, `UPDATE` o `NO_CHANGE` y explica el delta. Sin línea base verificable, bloquea. |

## Entradas
Obligatorias:
1. **Repositorio del microservicio**: ruta local o referencia (rama y commit).
2. **Contrato de la API**: `api.yaml` u OpenAPI en el repositorio. Sin contrato, bloquear.
3. **TC aprobados** del microservicio: `TC-*` en `testing/<DSP>/[<SSP>]/TC/` o el índice `mapa-tc-microservicio.yaml`, con readiness `READY` en `coverage-matrix.yaml`. Un TC `BLOCKED_CLARIFICATION` o `DEFERRED` no entra en la colección; se reporta.
4. **Historias de usuario** de los TC (`requirements/context-packs/user-stories/`): fuente literal de los criterios de aceptación.
5. **Convención de variables**: `baseUrl`, y un token por rol requerido por los TC (`tokenXxx`). Los tokens nunca se escriben en el archivo.

Ausencias y conflictos:
- Un TC sin ID oficial no se inventa. Se usa `TC-<SIGLAS-MS>-NN` con la marca `provisional` en la descripción de la carpeta y se reporta en la salida.
- Un AC que no existe en la historia se documenta como ausente; no se redacta un criterio nuevo.
- Un criterio que el TC cita pero la historia no define (por ejemplo, paginación sin AC propio) se documenta con esa nota explícita.

## Procedimiento
1. **Validar entradas.** Verificar que el contrato, los TC y las historias existen y que los TC están `READY`. Registrar lo excluido y su motivo.
2. **Agrupar por funcionalidad.** Mapear cada TC a un endpoint (operationId del contrato). Un TC que cubre varios endpoints se asigna al endpoint principal y se referencia desde los demás.
3. **Construir la estructura.** Crear `RF##` por funcionalidad en orden de número de requisito. Dentro, una carpeta por TC con nombre `<ID> - <Nombre>`. Las descripciones de carpeta llevan la trazabilidad (`Cubre <AC>`, historia y TSN).
4. **Crear los requests.** Un request por caso de prueba del TC: cada `Precondición`, `Datos de prueba` y `Resultado esperado (oracle)` se traduce en una aserción. Usar `{{baseUrl}}` y variables de rol.
5. **Documentar cada request.** En `request.description` escribir `**Objetivo:**`, `**Caso:**` y `**Criterios de aceptación:**`. Los criterios se extraen por script desde la historia (título y bloque Gherkin), no se transcriben a mano. Ver `references/estructura-coleccion.md`.
6. **Registrar huecos.** Por cada AC sin request, anotar el motivo (bloqueado por decisión, requiere otro token, requiere datos sembrados, etc.).
7. **Validar estructura.** Ejecutar `python scripts/validar_coleccion.py <ruta>` y corregir los hallazgos antes de entregar.
8. **Ejecutar si es posible.** Si hay URL del ambiente y tokens, ejecutar `newman run` y registrar el resultado. Si no, registrar `NOT_EXECUTED` con la razón.
9. **Entregar.** Escribir `test/functional/postman.json` y el reporte de consolidación (ver Salida).

## Salida
- `test/functional/postman.json`: colección Postman v2.1.
- `postman-automation-report.yaml`: payload operativo para el orquestador (no es un documento OKF; no lleva metadatos OKF). Contiene:
  - `microservicio`, `contrato`, `modo`, `rama`, `commit`;
  - `funcionalidades`: lista de `RF##`;
  - `casos`: por cada TC, `id`, `estado` (`AUTOMATED`, `PARTIAL`, `NOT_AUTOMATED`), requests asociados;
  - `acs_sin_automatizar`: AC, motivo y dueño de la decisión;
  - `variables_requeridas`;
  - `newman`: objeto con `estado` (`EXECUTED` o `NOT_EXECUTED`) y, según el caso, `resultados` (totales de requests, aserciones y fallos) o `razon`. El check `api-automation-subordinate-traceable` lee `newman.estado`.

Completitud: todo TC `READY` aparece en el reporte con un estado, y todo request tiene documentación.

## Modo subordinado (T05-API)
Lo invoca `qa-agentic-test-engineer` dentro de la tarea `T05-API` del plan de `qa-sdlc-orchestrator`. Entradas adicionales:
- `plan_id`, `dsp_id` y `ssp_id` (alcance del plan; el SSP es opcional);
- los TC funcionales de su subordinado (un microservicio, `tc_funcional` del scope), `READY`;
- la ruta del pack de ingeniería de destino.

Salidas:
- `test/functional/postman.json` en el repositorio del microservicio.
- `<pack>/automated-tests/postman/<microservicio>/postman-automation-report.yaml`, con `casos[].id` igual al `testcase_ref` de cada AT, `casos[].estado` (`AUTOMATED`, `PARTIAL` o `NOT_AUTOMATED`) y `newman.estado`.

No escribe AT-*, EXEC ni el gate: eso corresponde al engineer. La ejecución newman (E6) se convierte en evidencia del check `api-automation-subordinate-traceable` del engineer; el skill no emite PASS por sí mismo.

## Gate y evidencia
| Check | Criterio | Tipo |
|---|---|---|
| E1 Entradas | Contrato, TC `READY` e historias disponibles | script + revisión |
| E2 Estructura | Carpetas `RF##-` y `<ID> - <Nombre>`, sin `AC-` en títulos de carpeta | script (`validar_coleccion.py`) |
| E3 Documentación | Cada request con objetivo, caso y criterios (o nota explícita) | script |
| E4 Sin secretos | Ningún token ni JWT literal en el archivo | script |
| E5 Trazabilidad | Todo TC `READY` tiene carpeta o motivo de exclusión en el reporte | revisión |
| E6 Ejecución | Newman ejecutado contra el ambiente con los tokens | evidencia externa |

Resultados: `PASS`, `UNCERTAIN` o `FAIL`. E6 `NOT_EXECUTED` impide un `PASS` total y se declara como pendiente; no se presenta como validado. El skill nunca emite la aprobación del gate; eso lo decide el orquestador.

## Restricciones
- No hacer `push` ni crear ramas en el repositorio del microservicio sin aprobación explícita de la persona que encarga la tarea.
- No escribir tokens, contraseñas ni URLs con credenciales. Usar variables.
- No inventar IDs de TC, criterios de aceptación ni datos sembrados.
- No afirmar cobertura ni validación que no se ejecutó.
- No modificar archivos fuera de `test/functional/` y del reporte.
- Cambios de alcance (agregar o quitar funcionalidades) y excepciones a la estructura requieren decisión humana.

## Conformidad
- Guía de plugins y skills del catálogo (contrato de skill, gates y limitaciones declaradas).
- Estructura y nomenclatura: `references/estructura-coleccion.md`.
- Validación: `python scripts/validar_coleccion.py <ruta-a-postman.json>`. Código de salida `0` sin hallazgos, `1` con hallazgos, `2` si el archivo no se puede leer.
- Limitación declarada: el validador comprueba estructura, documentación y ausencia de secretos. No comprueba que los criterios coincidan con la historia ni que las aserciones sean correctas; eso exige revisión humana y ejecución en ambiente.
