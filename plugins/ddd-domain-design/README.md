# DDD Domain Design Plugin v1.2.1

Anthropic Claude Code plugin with six DDD specialist skills and one orchestrator.

Documentación completa (skills, secuencia, entregables y gates): [DOCUMENTACION.md](DOCUMENTACION.md).

## Installation
```bash
python -m pip install PyYAML
# Recomendado: instalar desde el marketplace comsatel-skills-catalog
# Desarrollo local: claude --plugin-dir ./plugins/ddd-domain-design
```

Invoke `/ddd-domain-design:ddd-design-orchestrator` (plugin name is defined in `.claude-plugin/plugin.json`).

**Escenarios:** el plugin se usa igual en Greenfield, Brownfield y Evolution: `workflow.py init` no recibe `--scenario` y ninguno de sus seis skills reconstruye el dominio desde código existente. En un componente existente, la reconstrucción As-Is la aporta `microservice-api-design` (tipo `ASIS`) y sus resultados se usan como fuentes verificadas (`scope-manifest.yaml`) de `ddd-domain-discovery`; la comparación con el dominio actual depende de la revisión humana en los gates.

## Local workflow CLI
```bash
python scripts/workflow.py init .comsatel/ddd-domain-design/runs/RUN-001 --scope DSP-001 --workspace .
# Edit .comsatel/ddd-domain-design/runs/RUN-001/scope-manifest.yaml with verified approved sources
python scripts/workflow.py check .comsatel/ddd-domain-design/runs/RUN-001
python scripts/workflow.py approve-gate .comsatel/ddd-domain-design/runs/RUN-001 --gate G0 --actor 'human:reviewer' --evidence 'approval-reference'
python scripts/workflow.py transition .comsatel/ddd-domain-design/runs/RUN-001 --task T01 --to READY --actor orchestrator --reason 'G0 approved'
python scripts/workflow.py status .comsatel/ddd-domain-design/runs/RUN-001
python scripts/workflow.py validate-contract .comsatel/ddd-domain-design/runs/RUN-001/artifacts/domain-design-contract.yaml --run .comsatel/ddd-domain-design/runs/RUN-001
```

`approve-gate` records a human approval claim but does not verify identity. Never invoke without explicit approval. Workflow scripts are advisory/local, not concurrency-safe. Gate ordering is G0 scope, G1 context boundaries, G2 tactical/event model, G3 contracts, G4 handoff. The baseline DAG can be customized before G0, and should be checked after changes.

## Content contracts
Use Markdown OKF v0.2 frontmatter according to enterprise conventions; `domain-design-contract.yaml` is machine-readable interoperability output for downstream API/Microservice and Data packs. Semantic validation and review remain mandatory.

## v0.4.0 — STD-OKF-001 v1.1.0
La norma corporativa está incluida en `standards/`. Los documentos conceptuales pasan por tres niveles: `okf`, `profile` y `publish`. Los documentos de progreso YAML son operativos y no deben llevar frontmatter OKF.

```bash
python scripts/okf_validate.py skills/ddd-bounded-context-designer/templates/bounded-context-okf.md --level profile
python scripts/okf_validate.py skills/ddd-context-map-designer/templates/context-map-okf.md --level profile
python scripts/okf_validate.py runs/<run-id>/artifacts/bounded-contexts.md --level publish --run runs/<run-id>
```

**Limitación:** el validador de publicación comprueba evidencia declarada y gates en archivos locales, pero no autentica al aprobador ni ejecuta un render real de Mermaid. La aprobación efectiva debe integrarse con controles protegidos de GitLab.


Actualización v0.4.0: catálogo AGG/VO/EVT aprobado; plantillas y validación de tipos DDD incluidos.

## Output Pathmap (pathmap_version 1.0.0)

El orchestrator consulta `assets/pathmap.md`/`assets/pathmap.json` en G0 y transmite rutas absolutas derivadas de `workspace_root` a cada skill. Los artefactos de dominio van a `./architecture/` por tipo; los registros operativos a `.comsatel/ddd-domain-design/runs/<run-id>/`. Ejemplo: `python scripts/workflow.py init <workspace>/.comsatel/ddd-domain-design/runs/RUN-001 --scope DSP-001 --workspace <workspace>`. Los gates siguen sujetos a aprobación humana.
