---
name: web-automation
description: Usar cuando los TC aprobados de superficie WEB de un AUT (Shell de micro-frontends o aplicación web) deban implementarse como pruebas Playwright o Selenium en test/functional/, con un reporte por AUT y sin datos ni credenciales en el repositorio.
metadata:
  version: "1.0.0"
  author: "COMSATEL"
  type: "qa"
---
# Web Automation

## Propósito
Implementar, para **un AUT web**, los TC aprobados de superficie `WEB` como pruebas automatizadas dentro del repositorio del AUT:

- **Shell de micro-frontends:** el AUT es el Shell. Los TC se ejecutan contra el Shell y los micro-frontends que compone; no se crea un AUT por cada micro-frontend.
- **Aplicación web legada:** el AUT es la aplicación web específica.

El framework (Playwright o Selenium) lo declara el documento `WEB` del AUT en la KB. Este skill no lo elige por su cuenta. Si el documento no lo declara, bloquea.

El skill escribe código y su reporte. No ejecuta el pipeline ni decide el gate: la ejecución la hace la CI del AUT al abrir el MR, y el gate lo decide el orquestador.

## Activación y alcance
Usar cuando:
- existe un `QTD` con TC `READY` de superficie `WEB` asignados a este AUT;
- el AUT tiene documento `WEB` en la KB con framework declarado;
- lo invoca `qa-agentic-test-engineer` desde `T05-WEB`, como subordinado.

Exclusiones:
- TC de superficie `API`: los implementa `postman-automation` o `loadtest-automation`.
- TC de superficie `MOBILE`: se implementan en la suite Appium del AUT móvil.
- TC manuales (`automation_status: MANUAL_ONLY`): no se automatizan.
- Pruebas de carga web: fuera de alcance en esta versión.

## Modo subordinado (T05-WEB)
Lo invoca `qa-agentic-test-engineer` con:
- `plan_id`, `dsp_id` y `ssp_id` (el SSP es opcional);
- el AUT (ID del documento `WEB` en la KB) y su framework declarado;
- los TC web `READY` asignados a ese AUT;
- la ruta del repositorio del AUT (rama y commit base).

Salidas:
- código en `test/functional/<framework>/` del repositorio del AUT, en una rama con MR;
- `<pack>/automated-tests/web/<aut>/web-automation-report.yaml`, validado con `scripts/validar_reporte_web.py`.

El reporte lo lee el check `web-automation-subordinate-traceable`: cada AT de superficie `WEB` debe aparecer en `casos` con estado `AUTOMATED` o `PARTIAL`, y `ejecucion.estado` debe ser `EXECUTED`.

## Procedimiento
1. **Validar entradas.** Confirmar que el documento `WEB` del AUT existe en la KB, declara framework y que los TC están `READY`. Si falta el framework, bloquear.
2. **Revisar la suite existente.** Si el repositorio ya tiene `test/functional/<framework>/`, leer sus page objects, fixtures y configuración antes de escribir. Reutilizar lo que exista; no regenerar la suite.
3. **Un caso por TC.** Cada TC web se implementa como un test, con su `TC-ID` en el nombre o en una etiqueta. Sin etiqueta de TC no hay trazabilidad, y el test no cuenta.
4. **Aplicar el oracle del TC.** Cada resultado esperado del TC se traduce en una aserción. No se relaja el oracle ni se cambia el TC.
5. **Datos y credenciales por referencia.** Los datos vienen del `TDA` del run o de variables de entorno. Nunca se escriben credenciales, tokens ni URLs con credenciales en el repositorio.
6. **Registrar huecos.** Cada TC sin implementación se anota en `acs_sin_automatizar` con el motivo.
7. **Validar el reporte.** Ejecutar `python scripts/validar_reporte_web.py <reporte>` y corregir los hallazgos antes de entregar.
8. **Entregar.** Crear la rama con el código y el MR. El reporte lleva `ejecucion.estado: NOT_EXECUTED` hasta que el pipeline del MR termine; el engineer lo actualiza con la evidencia del pipeline.

## Salida: reporte
`web-automation-report.yaml` es un payload operativo, no un documento OKF. Contiene:
- `aut`: ID del documento `WEB` en la KB;
- `framework`: `PLAYWRIGHT` o `SELENIUM`;
- `rama` y `commit`;
- `casos`: lista de `{id, estado, archivos}` con `id` igual a un `TC-*`, `estado` en `AUTOMATED`, `PARTIAL` o `NOT_AUTOMATED`, y las rutas de sus archivos;
- `acs_sin_automatizar`: lista de criterios sin prueba, con motivo;
- `ejecucion`: `{estado, pipeline, resultados, razon}`. `estado` es `EXECUTED` o `NOT_EXECUTED`. Si es `EXECUTED`, `pipeline` y `resultados` son obligatorios. Si es `NOT_EXECUTED`, `razon` es obligatoria. El pipeline se registra solo con el ID o la URL reales.

## Gate y evidencia
| Check | Criterio | Tipo |
|---|---|---|
| W1 Entradas | Documento `WEB` con framework declarado y TC `READY` | script + revisión |
| W2 Estructura | Reporte válido según `validar_reporte_web.py` | script |
| W3 Trazabilidad | Cada TC web aparece en `casos` con `AUTOMATED` o `PARTIAL` | script (`web-automation-subordinate-traceable`) |
| W4 Ejecución | `ejecucion.estado` es `EXECUTED`, con pipeline real | script (`web-automation-subordinate-traceable`) |
| W5 Sin secretos | Ningún token, contraseña ni URL con credenciales | script |

Un reporte con `NOT_EXECUTED` impide un `PASS` total y se declara pendiente; no se presenta como validado. El skill nunca emite la aprobación del gate.

## Restricciones
- No hacer `push` ni crear ramas en el repositorio del AUT sin aprobación explícita de quien encarga la tarea. El cambio llega por MR.
- No modificar el TC ni relajar su oracle.
- No escribir credenciales, tokens ni URLs con credenciales.
- No inventar identificadores de pipeline, de TC ni de criterios.
- No modificar archivos fuera de `test/functional/<framework>/` y del reporte.
- Cambios de alcance y excepciones a la estructura requieren decisión humana.

## Conformidad
- Estructura de la suite y del reporte: `references/estructura-web.md`.
- Validación del reporte: `python scripts/validar_reporte_web.py <reporte>`. Código de salida `0` sin hallazgos, `1` con hallazgos, `2` si el archivo no se puede leer.
- Limitación declarada: el validador comprueba estructura, campos obligatorios y ausencia de secretos. No comprueba que las aserciones reproduzcan el oracle del TC ni que la ejecución en el pipeline haya pasado; eso exige revisión humana y la evidencia del pipeline.
