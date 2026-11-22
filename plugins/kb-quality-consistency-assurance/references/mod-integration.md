# KB-QCA Mod integration (v1.1.0)

## Scope
- **Knowledge Governance Guard:** observa patrones de comandos Bash potencialmente destructivos. No bloquea ni autoriza herramientas.
- **Señales explicadas:** cada señal tiene un id de regla (`R-01` a `R-04`), un motivo y una acción sugerida.
- **Quality Gate Monitor:** `/kb-quality-status` informa las señales agrupadas por regla y el catálogo de gates. `/kb-quality-status all` muestra todas las señales guardadas. El estado real de G1–G6 **no está conectado** en esta versión.
- **Panel de señales:** `/kb-quality-risks` abre un panel de solo lectura con las reglas activas, su acción sugerida y las señales recientes.
- `ui.render` añade al spinner el número de señales y la regla más frecuente.

## Reglas
| Id | Detecta | Acción sugerida |
|---|---|---|
| R-01 | Git force push (`--force`, `-f`, `--force-with-lease`) | Usa `--force-with-lease` solo en tu rama y confirma que nadie más trabaja en ella. |
| R-02 | Reescritura de historia (`reset --hard`, `filter-branch`) | Revisa `git status` y `git log` antes; para deshacer un commit publicado, prefiere `git revert`. |
| R-03 | `rm` recursivo y forzado | Revisa la ruta objetivo antes de ejecutar y evita `-f` si no es necesario. |
| R-04 | Push directo a `main`, `master` o `develop` | Sube a una rama de trabajo y abre un Merge Request. |

## Qué se guarda de cada señal
- Id de regla, hora, número de llamada de la sesión y un detalle redactado.
- El detalle conserva verbos, banderas y ramas protegidas. URLs, `usuario@host` y asignaciones (`clave=valor`) se ocultan, y el resto de argumentos solo se cuenta (`· 2 argumento(s) oculto(s)`).
- Nunca se guardan comandos completos, rutas ni contenido de documentos.

## Limitaciones
- No inspecciona operaciones realizadas por otras herramientas, API remotas o comandos encapsulados.
- Los patrones de detección son heurísticos: pueden generar falsos positivos y falsos negativos.
- Los eventos quedan en memoria de la sesión: se guardan las últimas 100 señales y se pierden al reiniciar.
- Nunca inferir un gate `PASS` a partir de la ausencia de señales.
- El panel es de solo lectura y se abre con un comando; no se abre solo al iniciar la sesión.

## Futura fase de enforcement
Requiere política explícita por repositorio, gate-state autenticado, tests de permisos y aprobación humana; jamás utilizar la capacidad del Mod para autoaprobar herramientas.

## Pruebas
- `node tests/mod-risk-patterns.test.mjs`: detectores, redacción, agrupación y límite de señales. No requiere dependencias.
- `tests/kb-governance-mod.test.ts` requiere el arnés de pruebas del engine; no se ejecutó en esta revisión.

## Seguridad
Los Mods tienen permisos de usuario. Revisar código, usar managed settings y conservar GitLab CI como control final.
