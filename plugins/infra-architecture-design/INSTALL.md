# Installation

```bash
claude --plugin-dir ./plugins/infra-architecture-design
```

Then run `/infra-architecture-design:infrastructure-plan` and supply mode and Context Packs, or just ask for infrastructure design: the `infrastructure-orchestrator` skill is the entry point.

Requirements: Python 3 with PyYAML for `workflow.py` and `validate.py`. Run `python -m unittest discover -s tests -v` to test the plan engine.
