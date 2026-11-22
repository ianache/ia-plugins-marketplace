"""Pruebas estructurales declaradas para ssp-closure; ejecutar solo bajo solicitud."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "scripts"
WORKFLOW = str(SCRIPTS / "workflow.py")
sys.path.insert(0, str(SCRIPTS))
import check_closure as cc  # noqa: E402


def okf_doc(doc_type: str, document_id: str) -> str:
    return f'''---
type: {doc_type}
id: "{document_id}"
title: Documento de prueba
description: Descripción verificable
version: "1.0.0"
status: draft
owner: "role:delivery-manager"
classification: internal
tags: [ssp, test]
product: CL2
pack: ssp-closure
skill: ssp-closure-orchestrator
related:
  - SSP-001
generated:
  by: "ssp-closure-orchestrator/1.0.0"
  at: "2026-11-15T10:00:00-05:00"
sources:
  - resource: "gitlab:#123"
    title: Fuente
---
# Documento
Historia #123; resultados observados.
'''


class OkfTests(unittest.TestCase):
    def test_status_report_accepts_approved_type_and_metadata(self):
        self.assertEqual(cc.check_status_report(okf_doc("STR", "STR-2026-W46")), [])

    def test_status_report_rejects_hours(self):
        self.assertTrue(any("C6" in e for e in cc.check_status_report(okf_doc("STR", "STR-W46") + "12 hours")))

    def test_rejects_unapproved_type(self):
        errors = cc.check_okf(okf_doc("RRD", "RRD-001"), "STR")
        self.assertTrue(any("type" in e for e in errors))

    def test_closure_requires_lessons_and_sections(self):
        text = okf_doc("CLS", "CLS-SSP-001") + "\n## Lecciones aprendidas\n## Transferencia\n## Resultado frente al objetivo\n## Aceptación y desviaciones\n"
        self.assertEqual(cc.check_closure_report(text), [])


class PayloadTests(unittest.TestCase):
    def test_review_agenda_requires_product_owner_and_blank_decision(self):
        self.assertEqual(cc.check_review_agenda("Product Owner registra. Decisión: ____"), [])
        self.assertTrue(cc.check_review_agenda("Decisión: Aceptada"))

    def test_retro_agenda_requires_hypotheses(self):
        self.assertTrue(cc.check_retro_agenda("Problema: demoras."))
        self.assertEqual(cc.check_retro_agenda("Hipótesis: falla de entorno."), [])

    def test_experiment_json_requires_owner_metric_and_date(self):
        payload = json.dumps({"owner_person": "Ana", "success_metric": "lead time", "due_date": "2026-12-01"})
        self.assertEqual(cc.check_experiment(payload), [])


class WorkflowTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, WORKFLOW, *args], capture_output=True, text=True)

    def test_init_status_and_approval_use_dot_comsatel_run_root(self):
        with tempfile.TemporaryDirectory() as root:
            init = self.run_cli("init", "RUN-1", "--root", root, "--project-id", "10", "--ssp-id", "SSP-1", "--period", "2026-W46")
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            run = Path(root) / ".comsatel/ssp-closure/runs/RUN-1"
            manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["product_lifecycle_mode"], "not-applicable")
            self.assertTrue((run / "task-results/T1").is_dir())
            self.assertTrue((run / "evidence/REVIEW_AGENDA_GATE").is_dir())
            self.assertEqual(self.run_cli("status", "RUN-1", "--root", root).returncode, 0)
            proposal = self.run_cli("propose-gate", "RUN-1", "--gate", "REVIEW_AGENDA_GATE", "--result", "READY", "--check", "agenda completa", "--evidence", "agenda.md", "--root", root)
            self.assertEqual(proposal.returncode, 0, proposal.stdout + proposal.stderr)
            approved = self.run_cli("approve-gate", "RUN-1", "--gate", "REVIEW_AGENDA_GATE", "--actor", "human:owner", "--evidence", "decision-ref", "--root", root)
            self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
            register = json.loads((run / "gate-register.json").read_text(encoding="utf-8"))
            self.assertTrue(register["gates"]["REVIEW_AGENDA_GATE"]["approved"])
            self.assertFalse(register["gates"]["REVIEW_AGENDA_GATE"]["actor_authenticated_by_script"])

    def test_rejects_path_traversal_and_run_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            bad = self.run_cli("init", "../outside", "--root", root, "--project-id", "10", "--ssp-id", "SSP-1", "--period", "W46")
            self.assertNotEqual(bad.returncode, 0)
            good = self.run_cli("init", "RUN-2", "--root", root, "--project-id", "10", "--ssp-id", "SSP-1", "--period", "W46")
            self.assertEqual(good.returncode, 0)
            again = self.run_cli("init", "RUN-2", "--root", root, "--project-id", "10", "--ssp-id", "SSP-1", "--period", "W46")
            self.assertNotEqual(again.returncode, 0)


if __name__ == "__main__":
    unittest.main()
