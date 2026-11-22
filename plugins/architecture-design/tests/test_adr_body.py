import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_adr_body import check
import validate_okf

FIXTURE = (ROOT / 'tests/fixtures/adr-valid.md').read_text(encoding='utf-8')
TEMPLATE = ROOT / 'skills/architecture-decision-governor/templates/okf-artifact.md'
APPROVED_ADR_TYPE = 'ADR'


def run(text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'adr.md'
        path.write_text(text, encoding='utf-8')
        return check(path)


class AdrBodyTests(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(run(FIXTURE), [])

    def test_template_is_rejected_until_completed(self):
        errors = check(TEMPLATE)
        self.assertTrue(errors)
        self.assertTrue(any('plantilla sin completar' in e for e in errors))

    def test_non_adr_is_skipped(self):
        self.assertIsNone(run(FIXTURE.replace('type: ADR', 'type: ASR', 1)))

    def test_missing_visual_section_fails(self):
        text = FIXTURE.replace('## Representación visual', '## Otra cosa', 1)
        self.assertTrue(any('Representación visual' in e for e in run(text)))

    def test_visual_exception_needs_motive(self):
        start = FIXTURE.index('## Representación visual')
        end = FIXTURE.index('## Evaluación ATAM')
        exception = '## Representación visual\n\nVisual: no aplica — decisión de licencia sin estructura ni flujo.\n\n'
        self.assertEqual(run(FIXTURE[:start] + exception + FIXTURE[end:]), [])
        no_motive = exception.replace('decisión de licencia sin estructura ni flujo.', '')
        self.assertTrue(any('sin diagrama Mermaid' in e for e in run(FIXTURE[:start] + no_motive + FIXTURE[end:])))

    def test_element_in_diagram_needs_catalog_row(self):
        text = FIXTURE.replace('E03 --> E06', 'E03 --> E07\n    E07["E07 Extra"]', 1)
        errors = run(text)
        self.assertIn('E07 aparece en el diagrama sin fila en el catálogo', errors)

    def test_catalog_row_needs_diagram_node(self):
        text = FIXTURE.replace('| E06 | Base de datos |', '| E08 | Base de datos |', 1)
        errors = run(text)
        self.assertIn('E06 aparece en el diagrama sin fila en el catálogo', errors)
        self.assertIn('E08 está en el catálogo sin nodo en el diagrama', errors)

    def test_variation_point_needs_table_row(self):
        text = FIXTURE.replace('| VP-02 | Motor de base de datos |', '| VP-09 | Motor de base de datos |', 1)
        errors = run(text)
        self.assertIn('VP-02 referenciado en el catálogo sin fila en "Puntos de variación"', errors)
        self.assertIn('VP-09 no está referenciado por ningún elemento del catálogo', errors)

    def test_variation_point_needs_responsible_and_binding_time(self):
        text = FIXTURE.replace('| VP-01 | Motor de caché | Redis, Memcached | despliegue | Redis | [PENDIENTE] | Sensibilidad: latencia de acierto |',
                               '| VP-01 | Motor de caché | Redis, Memcached | en algún momento | Redis |  | Sensibilidad: latencia de acierto |', 1)
        errors = run(text)
        self.assertIn('VP-01: momento de vinculación no reconocido', errors)
        self.assertIn('VP-01: falta responsable', errors)

    def test_atam_missing_type_needs_justification(self):
        text = FIXTURE.replace('| No-riesgo | N-01 |', '| Otro | N-01 |', 1)
        self.assertTrue(any('ATAM sin registros de tipo No-riesgo' in e for e in run(text)))
        justified = text.replace('## Consecuencias', 'Sin registros de tipo No-riesgo: no se identificó ninguno.\n\n## Consecuencias', 1)
        self.assertFalse(any('ATAM sin registros de tipo No-riesgo' in e for e in run(justified)))

    def test_atam_must_reference_existing_scenario(self):
        text = FIXTURE.replace('| Riesgo | R-01 | Si el motor de caché cae, la carga pasa a la base de datos | QA-03 |',
                               '| Riesgo | R-01 | Si el motor de caché cae, la carga pasa a la base de datos | QA-99 |', 1)
        self.assertTrue(any('debe referenciar un QA-nn existente' in e for e in run(text)))

    def test_scenario_needs_response_measure(self):
        text = FIXTURE.replace('| [PENDIENTE: arquitecto] | [PENDIENTE] |\n| QA-02', '|  | [PENDIENTE] |\n| QA-02', 1)
        self.assertTrue(any('QA-01: falta la medida de respuesta' in e for e in run(text)))

    def test_missing_frontmatter_is_reported(self):
        self.assertEqual(run('# sin frontmatter'), ['missing YAML frontmatter'])


class TemplateTypeTests(unittest.TestCase):
    """Each skill template declares the approved type its skill produces (STD-OKF-001 v1.4.0). ADR belongs only to the decision governor."""

    EXPECTED = {
        'architecture-asr-and-solution-designer': 'ASR',
        'architecture-context-and-evidence-designer': 'ACP',
        'architecture-conformance-assessor': 'CFR',
        'architecture-decision-governor': APPROVED_ADR_TYPE,
        'architecture-development-handoff': 'ADH',
        'architecture-evolution-governor': 'GOV',
    }

    def type_of(self, skill):
        for line in (ROOT / 'skills' / skill / 'templates/okf-artifact.md').read_text(encoding='utf-8').splitlines():
            if line.startswith('type:'):
                return line.split(':', 1)[1].strip().strip('"')
        return None

    def test_templates_declare_approved_types(self):
        for skill, expected in self.EXPECTED.items():
            self.assertEqual(self.type_of(skill), expected, skill)
            self.assertIn(expected, validate_okf.APPROVED, skill)

    def test_only_decision_governor_uses_adr(self):
        for skill in self.EXPECTED:
            if skill != 'architecture-decision-governor':
                self.assertNotEqual(self.type_of(skill), APPROVED_ADR_TYPE, skill)

    def test_orchestrator_has_no_okf_template(self):
        self.assertFalse((ROOT / 'skills/architecture-design-orchestrator/templates/okf-artifact.md').exists())


class PluginVersionTests(unittest.TestCase):
    def test_manifest_version_is_1_4_0(self):
        manifest = json.loads((ROOT / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['version'], '1.4.0')


if __name__ == '__main__':
    unittest.main()
