# Architecture Design — Claude Code Plugin v1.2.1

Rediseño de 30 skills originales en **6 skills especializados + 1 orchestrator**. El archivo `COVERAGE-MATRIX.md` demuestra la asignación completa. Los archivos originales ya no se incluyen en el plugin.

Documentación completa (skills, secuencia, entregables y gates): [DOCUMENTACION.md](DOCUMENTACION.md).

## Instalación
Descomprimir en una carpeta y cargar mediante el mecanismo de plugins de Claude Code compatible con el entorno de instalación. El manifiesto está en `.claude-plugin/plugin.json` y los skills en `skills/<name>/SKILL.md`. No se ha probado el descubrimiento en un runtime Claude Code real.

## Workflows
`scripts/workflow.py` planifica cada escenario con su propia cadena de tareas y gates:

| Escenario | Cadena | Gates activos |
| :--- | :--- | :--- |
| `greenfield` | contexto → ASR/solución → decisiones → handoff | G0, G1, G2, G3, G6 |
| `brownfield` | reconstrucción As-Is → análisis → decisiones → conformidad → handoff | G0, G1, G2, G3, G4, G6 |
| `evolution` | contexto + cambio → impacto → decisiones → conformidad/drift → gobierno → handoff | G0 a G6 |

`continuous-governance` se acepta como alias de `evolution`. Los gates G4 y G5 son condicionales: si el escenario los omite, el plan registra la omisión y G6 no se aprueba hasta justificarla.

```bash
python scripts/workflow.py init --root <workspace> --run-id RUN-001 --scenario brownfield
python scripts/workflow.py check --root <workspace> --run-id RUN-001
python scripts/workflow.py approve-gate --root <workspace> --run-id RUN-001 --gate G0 --actor human:<nombre> --evidence <ref>
python scripts/workflow.py transition --root <workspace> --run-id RUN-001 --task T01 --to READY --actor orchestrator --reason "G0 aprobado"
python scripts/workflow.py transition --root <workspace> --run-id RUN-001 --task T01 --to NEEDS_REVIEW --actor orchestrator --reason "entregado" --manifest <output-manifest.json>
python scripts/workflow.py justify-omission --root <workspace> --run-id RUN-001 --gate G5 --text "<motivo>"
python scripts/workflow.py status --root <workspace> --run-id RUN-001
```

Cada tarea entra por el gate anterior al que cierra, y pasar a `NEEDS_REVIEW` o `DONE` exige el `output-manifest.json` del skill con su `producer` y `gate`. El actor de un gate debe ser `human:<nombre>`. El script valida orden y estructura; no autentica identidad ni aprueba nada por su cuenta.

## Archivos
- Operativos: `.comsatel/architecture-design/runs/<run-id>/`
- Conceptuales OKF v0.2: `architecture/`
- Estándar: `standards/STD-OKF-001-v1.11.0-stable.md`

## Validación
`python scripts/validate_okf.py <document.md>` valida frontmatter estructural. Los tipos de v1.3.0 están aprobados; `--allow-draft-types` se conserva solo por compatibilidad. Los templates contienen placeholders y **no deben publicarse sin completarlos**.

El validador no valida semántica, fuentes reales, Markdown links ni aprobación humana. Ningún script publica ni aprueba gates.


## Routing policy v1.2.0
See `assets/pathmap.md`. The orchestrator supplies a routing contract for each specialized output, creates `routing-contracts.json` under `.comsatel/architecture-design/runs/<run-id>/`, and rejects unmapped types. ADR/ASR folders are user-confirmed; C4/SEQ/API/DSP folders are proposed plugin conventions pending corporate pathmap review.
