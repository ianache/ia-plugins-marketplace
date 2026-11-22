# Scripts

- `qa_orchestrator.py`: controlador fail-closed (init, g0, authorize, start, complete, gate, human, reopen, invalidate, cancel, waive, status, verify-authorization). Requiere Python 3 y PyYAML.
- `gate_governance.py`: política determinista de gates (copia de la del Pack Factory).
- `publish_testcase_issues.py`: publica `TC-*` aprobados como issues `TestCase`; exige aprobación humana, `GITLAB_PAT` en runtime y admite `--dry-run`.
