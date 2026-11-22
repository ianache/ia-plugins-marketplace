import sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
sys.path.insert(0, str(HERE))
import check_uow_package as c  # noqa: E402
from pkgfixture import body, build, md  # noqa: E402


class Package(unittest.TestCase):
    def pack(self, mode="GREENFIELD", **over):
        t, root = build(mode, **over)
        self.addCleanup(t.cleanup)
        return root

    def res(self, root, profile, uow="UOW-001"):
        return {x["id"]: x["result"] for x in c.checks(root, profile, uow)}

    def test_valid_package_passes_every_profile_in_every_mode(self):
        for mode in ("GREENFIELD", "BROWNFIELD", "EVOLUTION"):
            root = self.pack(mode)
            for profile in ("context", "slice", "binding", "codebase", "agent-plan", "readiness"):
                r = self.res(root, profile)
                self.assertEqual(set(r.values()), {"PASS"}, (mode, profile, c.checks(root, profile, "UOW-001")))

    # ---- contexto
    def test_sources_must_be_versioned_and_claims_separated(self):
        root = self.pack(UCX={"sources": [{"id": "US-001", "resource": "x.md", "version": "latest"}]})
        self.assertEqual(self.res(root, "context")["sources-versioned"], "FAIL")
        root = self.pack()
        f = next(root.glob("UCX-*.md")); f.write_text(f.read_text(encoding="utf8").replace("## Supuestos", "## Otra"), encoding="utf8")
        self.assertEqual(self.res(root, "context")["claims-separated"], "FAIL")

    def test_empty_unknowns_section_fails(self):
        root = self.pack()
        f = next(root.glob("UCX-*.md")); t = f.read_text(encoding="utf8")
        f.write_text(t.replace("## Desconocidos y preguntas abiertas\ncontenido", "## Desconocidos y preguntas abiertas\n"), encoding="utf8")
        self.assertEqual(self.res(root, "context")["unknowns-listed"], "FAIL")

    def test_brownfield_and_evolution_need_baseline(self):
        for mode in ("BROWNFIELD", "EVOLUTION"):
            root = self.pack(mode, UCX={"baseline": {"ref": None, "commit": None}})
            self.assertEqual(self.res(root, "context")["mode-baseline-consistent"], "FAIL", mode)

    # ---- slice
    def test_every_criterion_is_covered_and_none_is_invented(self):
        root = self.pack(UOW={"acceptance_criteria": ["AC-1"]})
        self.assertEqual(self.res(root, "slice")["criteria-assigned-to-uow"], "FAIL")
        root = self.pack(UOW={"acceptance_criteria": ["AC-1", "AC-2", "AC-9"]})
        self.assertEqual(self.res(root, "slice")["criteria-assigned-to-uow"], "FAIL")

    def test_boundaries_need_includes_and_excludes(self):
        root = self.pack()
        f = next(root.glob("UOW-001-*.md")); t = f.read_text(encoding="utf8")
        f.write_text(t.replace("**Excluye**\n- baja de cliente\n", ""), encoding="utf8")
        self.assertEqual(self.res(root, "slice")["uow-boundaries-defined"], "FAIL")

    def test_uow_dependencies_must_be_acyclic_and_known(self):
        root = self.pack(UOW={"depends_on_uow": ["UOW-001"]})
        self.assertEqual(self.res(root, "slice")["dependencies-acyclic"], "FAIL")
        root = self.pack(UOW={"depends_on_uow": ["UOW-777"]})
        self.assertEqual(self.res(root, "slice")["dependencies-acyclic"], "FAIL")

    def test_uow_must_trace_to_a_us_in_the_context(self):
        root = self.pack(UOW={"us_ref": "US-999"})
        self.assertEqual(self.res(root, "slice")["uow-traces-to-us"], "FAIL")

    # ---- contratos
    def test_missing_or_unversioned_contracts_fail(self):
        root = self.pack(UCB={"api_operations": [], "data_objects": []})
        r = self.res(root, "binding")
        self.assertEqual((r["api-operations-resolved"], r["db-objects-resolved"]), ("FAIL", "FAIL"))
        root = self.pack(UCB={"api_operations": [{"operation_id": "createCustomer", "contract_ref": "API-001", "contract_version": "latest"}]})
        self.assertEqual(self.res(root, "binding")["contract-versions-pinned"], "FAIL")

    def test_not_applicable_requires_a_reason_and_is_accepted(self):
        root = self.pack(UCB={"api_operations": [], "api_not_applicable": "solo lógica interna", "data_objects": [], "data_not_applicable": "sin persistencia",
                              "api_fields": [], "mapping": []})
        r = self.res(root, "binding")
        self.assertEqual((r["api-operations-resolved"], r["db-objects-resolved"]), ("PASS", "PASS"))

    def test_every_api_field_needs_a_column_or_a_reason(self):
        root = self.pack(UCB={"api_fields": ["name", "email", "phone"]})
        self.assertEqual(self.res(root, "binding")["api-db-consistent"], "FAIL")
        root = self.pack(UCB={"api_fields": ["name", "email", "phone"], "mapping": [
            {"api_field": "name", "column": "customer.name"}, {"api_field": "email", "column": "customer.email"},
            {"api_field": "phone", "na_reason": "campo calculado en la capa de servicio"}]})
        self.assertEqual(self.res(root, "binding")["api-db-consistent"], "PASS")

    # ---- código
    def test_repository_reference_must_be_real(self):
        root = self.pack(UCM={"repository": {"project": "customers-svc", "target_branch": "develop", "source_ref": "develop", "source_commit": "HEAD"}})
        self.assertEqual(self.res(root, "codebase")["repo-ref-pinned"], "FAIL")
        root = self.pack(UCM={"repository": {"project": "customers-svc", "target_branch": "develop", "source_ref": "develop", "source_commit": "<sha>"}})
        self.assertEqual(self.res(root, "codebase")["repo-ref-pinned"], "FAIL")

    def test_paths_and_zones_are_mandatory(self):
        root = self.pack(UCM={"allowed_paths": [], "forbidden_paths": []})
        r = self.res(root, "codebase")
        self.assertEqual((r["allowed-paths-defined"], r["forbidden-zones-defined"]), ("FAIL", "FAIL"))

    def test_existing_code_analysis_is_required_outside_greenfield(self):
        for mode in ("BROWNFIELD", "EVOLUTION"):
            root = self.pack(mode, UCM={"existing_code_analysis": {"performed": False, "summary_ref": None}})
            self.assertEqual(self.res(root, "codebase")["baseline-analysis-present"], "FAIL", mode)
        root = self.pack("GREENFIELD", UCM={"existing_code_analysis": {"performed": False, "summary_ref": None}})
        self.assertEqual(self.res(root, "codebase")["baseline-analysis-present"], "PASS")

    # ---- plan del agente
    def test_implementation_steps_must_be_test_first_and_verifiable(self):
        steps = [{"id": "S-01", "kind": "impl", "goal": "alta", "files": ["a.py"], "test_first": False, "verify": "pytest", "expected": "pasa"}]
        root = self.pack(UAP={"steps": steps})
        self.assertEqual(self.res(root, "agent-plan")["tests-before-code"], "FAIL")
        steps = [{"id": "S-01", "kind": "test", "goal": "t", "files": ["a.py"], "test_first": True, "verify": "", "expected": "falla"}]
        root = self.pack(UAP={"steps": steps})
        self.assertEqual(self.res(root, "agent-plan")["steps-verifiable"], "FAIL")

    def test_stop_conditions_deviation_protocol_and_dod_are_required(self):
        root = self.pack(UAP={"stop_conditions": [], "deviation_protocol": {"escalate_to": ""}, "definition_of_done": []})
        r = self.res(root, "agent-plan")
        self.assertEqual((r["stop-conditions-defined"], r["deviation-protocol-present"], r["dod-measurable"]), ("FAIL", "FAIL", "FAIL"))

    def test_secrets_are_blocked_but_references_are_accepted(self):
        root = self.pack()
        f = next(root.glob("UOW-001/UAP-*.md")); t = f.read_text(encoding="utf8")
        f.write_text(t + "\nDB_PASSWORD: Sup3rSecret99\n", encoding="utf8")
        self.assertEqual(self.res(root, "agent-plan")["no-secrets"], "FAIL")
        f.write_text(t + "\nDB_PASSWORD: ref:vault/qa/db\n", encoding="utf8")
        self.assertEqual(self.res(root, "agent-plan")["no-secrets"], "PASS")

    # ---- revisión
    def test_package_must_be_complete_and_traceable(self):
        root = self.pack()
        next(root.glob("UOW-001/UAP-*.md")).unlink()
        r = self.res(root, "readiness")
        self.assertEqual((r["package-complete"], r["traceability-complete"]), ("FAIL", "FAIL"))
        root = self.pack()
        f = next(root.glob("UOW-001-*.md")); f.write_text(f.read_text(encoding="utf8").replace("## Handoff a QA", "## Otro"), encoding="utf8")
        self.assertEqual(self.res(root, "readiness")["package-complete"], "FAIL")

    def test_reviewer_must_be_independent_of_the_authors(self):
        root = self.pack(UWR={"reviewer": "agent:planner"})
        self.assertEqual(self.res(root, "readiness")["reviewer-independent-of-author"], "FAIL")
        root = self.pack(UWR={"reviewer": ""})
        self.assertEqual(self.res(root, "readiness")["reviewer-independent-of-author"], "FAIL")

    def test_blocking_open_questions_fail_unless_resolved_or_non_blocking(self):
        root = self.pack(UOW={"open_questions": [{"id": "Q-1", "status": "OPEN", "owner": "po"}]})
        self.assertEqual(self.res(root, "readiness")["open-questions-handled"], "FAIL")
        root = self.pack(UOW={"open_questions": [{"id": "Q-1", "status": "OPEN", "owner": "po", "blocking": False},
                                                 {"id": "Q-2", "status": "RESOLVED", "owner": "po"}]})
        self.assertEqual(self.res(root, "readiness")["open-questions-handled"], "PASS")

    def test_cli_errors_and_profiles_that_need_a_uow(self):
        self.assertEqual(c.main(["--root", "/no/existe", "--profile", "context"]), 2)
        self.assertEqual(c.main(["--root", str(self.pack()), "--profile", "binding"]), 2)


if __name__ == "__main__":
    unittest.main()


class CompatRollback(unittest.TestCase):
    """D-25: en EVOLUTION el UCM exige backward_compatibility y rollback (campo + sección); en otros modos no aplica."""

    def ids(self, mode, **over):
        t, root = build(mode, **over)
        self.addCleanup(t.cleanup)
        return {c["id"]: c for c in c.checks(root, "codebase", "UOW-001")}["compat-and-rollback-present"]

    def test_evolution_completo_pasa_y_otros_modos_no_aplican(self):
        for mode in ("GREENFIELD", "BROWNFIELD", "EVOLUTION"):
            self.assertEqual(self.ids(mode)["result"], "PASS", mode)

    def test_evolution_sin_campos_o_sin_secciones_falla(self):
        for over in ({"UCM": {"backward_compatibility": {"assessed": False, "summary": None}}},
                     {"UCM": {"rollback": {"defined": True, "summary": ""}}},
                     {"UCM": {"rollback": None}}):
            self.assertEqual(self.ids("EVOLUTION", **over)["result"], "FAIL", over)

    def test_evolution_sin_secciones_en_el_cuerpo_falla(self):
        t, root = build("EVOLUTION"); self.addCleanup(t.cleanup)
        f = next(root.rglob("UCM-001-alta.md"))
        f.write_text(f.read_text(encoding="utf8").split("## Compatibilidad")[0], encoding="utf8")
        r = {c["id"]: c for c in c.checks(root, "codebase", "UOW-001")}["compat-and-rollback-present"]
        self.assertEqual(r["result"], "FAIL")
