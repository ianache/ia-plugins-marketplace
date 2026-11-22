---
name: loadtest-automation
description: Usar cuando los TC de carga o rendimiento aprobados de un microservicio deban implementarse como suite Grafana k6 en su carpeta test/load, con un archivo principal k6.js, un módulo por caso, datos y configuración, sin umbrales inventados.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "qa"
---
# Load Test Automation

## Propósito
Convertir los TC aprobados con `test_type: rendimiento` de un microservicio en una suite Grafana k6 dentro de `codebase/<microservicio>/test/load/`:

- `k6.js`: archivo principal que ejecuta k6. Define `options` (escenarios y umbrales), importa los escenarios y los expone con `exec`.
- `scenarios/<TC-ID>.js`: un módulo por caso, con su función exportada y su lógica de carga.
- `lib/config.js`: lectura de variables de entorno (`API_URL`, `DEPLOYMENT_NAME`, credenciales por variable). Sin valores por defecto que sean secretos.
- `data/<dataset>.json` o `.csv`: datos de entrada, cargados con `SharedArray` o `open()` desde el módulo principal.
- `README.md`: cómo ejecutar, variables requeridas y criterio de la corrida.

El skill no decide umbrales: los toma de una fuente aprobada o deja la suite en modo BASELINE.

## Activación y alcance
Usar cuando:
- existen TC `READY` con `test_type: rendimiento` para un microservicio con superficie HTTP (API) o WebSocket;
- se pide crear o actualizar la suite k6 de ese microservicio.

Exclusiones:
- Microservicios sin API HTTP de negocio, que consumen solo eventos (Kafka): k6 no consume Kafka de forma nativa. Declarar `NOT_APPLICABLE` o `GAP` según corresponda; no sustituir la carga real por un health check y presentarlo como prueba de carga.
- Pruebas funcionales (las cubre `postman-automation`) y pruebas de integración Java.
- Escenarios de carga sin definición de carga (usuarios, duración o tasa): bloquear hasta que el TC las declare.

## Modos de criterio
Un umbral solo puede ser aprobado si tiene fuente. Por eso cada suite declara su criterio en la primera línea de `k6.js`:

| Criterio | Cuándo | Umbrales |
|---|---|---|
| `// criterio: BASELINE` | No hay cifra aprobada (por ejemplo, DATA-03 o DATA-04 abiertos en la norma de testing) | Ninguno. La corrida registra la línea base con `handleSummary`. Nunca declara aprobado ni fallido. |
| `// criterio: APROBADO <fuente>` | La cifra está aprobada y tiene identificador (DATA-xx, NFR-xx o el documento del requisito) | Cada umbral lleva un comentario `// umbral-fuente: <fuente>` en la línea anterior. |

Un umbral sin fuente, o un umbral en modo BASELINE, es un hallazgo.

## Entradas
Obligatorias:
1. **Repositorio del microservicio** (ruta local o referencia con rama y commit).
2. **TC aprobados de carga o rendimiento**: `TC-*` `READY` con su perfil de carga (usuarios virtuales, duración o tasa, rampa) y su criterio de aceptación.
3. **Fuente de umbrales**: identificador aprobado (DATA-xx, NFR-xx) o decisión de usar BASELINE. Sin fuente ni decisión, la suite queda en BASELINE.
4. **Contrato de la API** (`api.yaml` u OpenAPI) para los endpoints que el TC invoca.
5. **Datos de prueba** para los escenarios que lo requieran (con PII prohibida salvo autorización).

Ausencias y conflictos:
- Un TC sin perfil de carga no se implementa; se reporta como `BLOCKED_CLARIFICATION`.
- Un umbral del código que no coincide con la fuente aprobada se reporta, no se corrige en silencio.
- Un TC que pide un valor que la norma deja abierto se implementa en BASELINE y se declara.

## Procedimiento
1. **Validar entradas.** Comprobar TC `READY`, perfil de carga y fuente de umbrales. Registrar lo excluido.
2. **Definir el criterio.** Elegir BASELINE o APROBADO según la fuente. Escribirlo en la primera línea de `k6.js`.
3. **Crear un módulo por TC** en `scenarios/<TC-ID>.js`. Cada módulo exporta una función y no contiene URLs ni credenciales literales; usa `lib/config.js`.
4. **Ensamblar `k6.js`.** Declarar un escenario por TC en `options.scenarios` con `exec` igual al nombre exportado, y los umbrales (solo en APROBADO).
5. **Preparar datos** en `data/` y referenciarlos por ruta relativa.
6. **Documentar** en `README.md` el comando de ejecución y las variables requeridas.
7. **Validar.** Ejecutar `python scripts/validar_k6.py <ruta-a-test/load>` y corregir los hallazgos.
8. **Ejecutar si es posible.** Con `k6` instalado y ambiente autorizado, `k6 run` con las variables. Registrar el resumen. Si no, registrar `NOT_EXECUTED` con la razón.
9. **Entregar** la suite y el reporte de consolidación (ver Salida).

## Salida
- Suite en `codebase/<microservicio>/test/load/` (archivos listados en Propósito).
- `loadtest-automation-report.yaml` (un reporte por microservicio, en `automated-tests/k6/<microservicio>/` del pack): payload operativo para el orquestador (no es un documento OKF). Contiene:
  - `microservicio`, `contrato`, `criterio` (BASELINE o APROBADO con fuente), `rama`, `commit`;
  - `casos`: por cada TC, `id`, `estado` (`IMPLEMENTED`, `BLOCKED_CLARIFICATION`, `NOT_APPLICABLE`), escenario y archivo;
  - `gaps`: cargas no cubiertas y motivo (por ejemplo, consumo de Kafka sin cobertura);
  - `k6`: objeto con `estado` (`EXECUTED` o `NOT_EXECUTED`) y `resumen` o `razon`. El check `load-automation-subordinate-traceable` lee `k6.estado`.

## Gate y evidencia
| Check | Criterio | Tipo |
|---|---|---|
| L1 Estructura | `k6.js`, `scenarios/` y `lib/config.js` presentes; un módulo por TC | script |
| L2 Imports | Solo `k6`, `k6/*`, rutas relativas existentes o `https://jslib.k6.io` | script |
| L3 Cableado | Cada escenario en `options` tiene `exec` exportado desde `k6.js` | script |
| L4 Criterio | Primera línea con criterio; umbrales solo en APROBADO y con `umbral-fuente` | script |
| L5 Sin secretos | Sin URLs, tokens o contraseñas literales en el código | script |
| L6 Datos | Cada archivo de datos referenciado existe | script |
| L7 Ejecución | `k6` ejecutado con resumen en ambiente autorizado | evidencia externa |

Resultados: `PASS`, `UNCERTAIN` o `FAIL`. L7 `NOT_EXECUTED` impide declarar la suite validada; no se presenta como ejecutada. El skill no emite la aprobación del gate.

## Restricciones
- No inventar umbrales, perfiles de carga ni criterios de aceptación. Si la fuente no existe, la suite es BASELINE.
- No ejecutar contra producción ni contra ambientes sin autorización explícita. La carga sobre QA requiere confirmación de Infraestructura.
- No escribir tokens, contraseñas ni URLs con credenciales. Usar variables de entorno.
- No hacer `push` ni crear ramas en el repositorio del microservicio sin aprobación.
- No modificar archivos fuera de `test/load/` y del reporte.
- Cambios de perfil de carga o de criterio requieren decisión humana.

## Conformidad
- Estándar de pruebas de carga del proyecto (`STD-TEST-FLOTAS` §7): escenarios parametrizados, línea base y criterio de aprobación cuando se cierren los umbrales.
- Estructura y convenciones: `references/estructura-k6.md`.
- Validación: `python scripts/validar_k6.py <ruta-a-test/load>`. Código de salida `0` sin hallazgos, `1` con hallazgos, `2` si el directorio no se puede leer.
- Limitación declarada: el validador comprueba estructura, cableado, criterio, secretos y referencias. No comprueba que el perfil de carga sea el aprobado ni que la carga sea representativa; eso exige revisión humana y ejecución en ambiente.

## Modo subordinado (T05-API)
Lo invoca `qa-agentic-test-engineer` dentro de `T05-API`, igual que `postman-automation`, para los TC `rendimiento`. Su reporte lo verifica el check `load-automation-subordinate-traceable` del gate de ingeniería: criterio declarado, cada TC `IMPLEMENTED` y `k6.estado` `EXECUTED`. El skill no emite PASS.
