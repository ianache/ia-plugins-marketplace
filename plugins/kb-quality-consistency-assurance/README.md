# KB Quality & Consistency Assurance — Claude Code Plugin v1.2.1

Plugin experimental compatible con estructura de plugins de Claude Code: `.claude-plugin/plugin.json` + `skills/*/SKILL.md`.

**7 skills:** `kb-quality-orchestrator`, `kb-structure-validator`, `kb-reference-validator`, `kb-semantic-reviewer`, `kb-cross-artifact-reviewer`, `kb-change-impact-analyzer`, `kb-quality-reporter`.

## Instalación local
1. Descomprimir ZIP.
2. Ejecutar `claude --plugin-dir /ruta/kb-quality-consistency-assurance-plugin`.
3. Invocar el skill `kb-quality-orchestrator` para `audit`, `change-review` o `remediation`.

## Validación
`python -m unittest discover -s tests -v` (incluye `tests/test_mod_patterns.py`, que ejecuta `node tests/mod-risk-patterns.test.mjs` si hay Node.js). `tests/kb-governance-mod.test.ts` usa `claude-code/testing` y se ejecuta con `claude plugin test`.

## Límites
- No incluye conectores configurados ni acceso automático a GitLab/MCP/WebDAV; requieren permisos y endpoints reales.
- Los scripts validan la integridad del grafo; la validación OKF y semántica se ejecuta como instrucciones de skills y requiere documentos y políticas disponibles.
- `standards/STD-OKF-001-v1.11.0-stable.md` es la copia del estándar vigente (estable, aprobada). El informe usa el tipo `QAR` (KB Quality Report), aprobado en esa versión.
- Los ejemplos usan valores ficticios. El despliegue productivo requiere pruebas de integración y seguridad.

## Mod experimental (observe-only; versión propia del Mod 1.1.0, distinta de la del plugin)

Se incorpora `hooks/hooks.json` y `hooks/register.js` para Claude Code Mods.
- `/kb-quality-status`: resumen de observaciones y catálogo G1–G6 (estado de gates **no conectado**).
- Spinner: contador de señales potencialmente riesgosas.
- Señales que detecta (solo observa, no bloquea): `git push --force`/`-f`; `git reset --hard` y `filter-branch`; `rm` recursivo y forzado con las banderas en cualquier forma (`-rf`, `-fr`, `-r -f`, `-Rf`, `--recursive --force`); y `git push` hacia `main`, `master` o `develop` en cualquier forma de refspec (`origin main`, `HEAD:main`, `+main`, `refs/heads/main`, `--delete main`).
- Sin bloqueo, aprobación automática, publicación, lectura de secretos ni telemetría externa.
- Requisitos: Claude Code CLI >= 2.1.287. Validar con `claude plugin validate .` y `claude plugin test`.
- Desarrollo local: `claude --plugin-dir .` desde un workspace confiable.
- Revisar `references/mod-integration.md` antes de instalar.
