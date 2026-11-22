"""Contrato TestCase 1.4 (api_id): ejemplo válido, reglas negativas, schema coherente con el validador y compatibilidad legacy."""
import importlib.util
from pathlib import Path

import yaml

SK = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tc_detail', SK / 'scripts' / 'check_tc_detail.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

EXAMPLE = (SK / 'examples' / 'TC-API-017.md').read_text(encoding='utf-8')
TEMPLATE = (SK / 'templates' / 'TestCase-OKF.md').read_text(encoding='utf-8')
SCHEMA = yaml.safe_load((SK / 'resources' / 'schemas' / 'test-case.schema.yaml').read_text(encoding='utf-8'))


def mutate(old, new):
    assert old in EXAMPLE, 'la mutación no aplica: ' + old
    return EXAMPLE.replace(old, new, 1)


def test_example_is_valid_contract():
    assert mod.check(EXAMPLE) == []


def test_template_declares_every_contract_section_and_oracle_labels():
    for heading in mod.CONTRACT_SECTIONS:
        assert f'## {heading}' in TEMPLATE, heading
    for token in ('Pass when:', 'Fail when:', 'Idempotencia:', 'cleanup.required:', 'cleanup.strategy_ref:', 'MANUAL:', 'AUTOMATED_CICD:', 'allowed_environments:', 'forbidden_environments:'):
        assert token in TEMPLATE, token


def test_missing_intent_rejected():
    start = EXAMPLE.index('## Intención'); end = EXAMPLE.index('## Elemento bajo prueba')
    assert any('Intención' in i for i in mod.check(EXAMPLE[:start] + EXAMPLE[end:]))


def test_destructive_without_human_authorization_rejected():
    assert any('requires_human_authorization' in i for i in mod.check(mutate('destructive: false', 'destructive: true')))


def test_production_must_be_forbidden_and_never_allowed():
    assert any('PRODUCTION' in i for i in mod.check(mutate('forbidden_environments: PRODUCTION', 'forbidden_environments: none')))
    assert any('PRODUCTION' in i for i in mod.check(mutate('allowed_environments: QA, CERTIFICATION', 'allowed_environments: QA, PRODUCTION')))


def test_evidence_mode_without_value_rejected():
    assert any('AUTOMATED_CICD' in i for i in mod.check(mutate('- AUTOMATED_CICD: test_report, pipeline_job_reference, execution_log', '- AUTOMATED_CICD:')))


def test_traceability_must_match_frontmatter():
    assert any('tsn' in i for i in mod.check(mutate('- tsn: TSN-001', '- tsn: TSN-999')))


def test_step_referencing_undefined_test_data_rejected():
    assert any('TD-09' in i for i in mod.check(mutate('| TD-01, TD-02 | Respuesta HTTP 403', '| TD-09 | Respuesta HTTP 403')))


def test_undeclared_tdr_rejected():
    assert any('TDR-017-02' in i for i in mod.check(mutate('tdr_refs: [TDR-017-01, TDR-017-02]', 'tdr_refs: [TDR-017-01]')))


def test_oracle_without_fail_when_rejected():
    block = ('Fail when:\n- Se devuelve información del vehículo del Tenant B.\n'
             '- La solicitud responde con HTTP 2xx.\n'
             '- Se expone información de otro tenant en cualquier campo de la respuesta.\n')
    assert any('Fail when' in i for i in mod.check(mutate(block, 'Fail when:\n')))


def test_cleanup_required_needs_strategy():
    assert any('cleanup.strategy_ref' in i for i in mod.check(mutate('- cleanup.required: false\n- cleanup.strategy_ref: null', '- cleanup.required: true\n- cleanup.strategy_ref: null')))


def test_placeholder_left_unfilled_rejected():
    assert any('placeholders' in i for i in mod.check(mutate('Idempotencia: sí;', 'Idempotencia: TBD;')))


def test_invalid_enum_rejected():
    assert any('test_type' in i for i in mod.check(mutate('test_type: seguridad', 'test_type: funcional')))


def test_surface_target_attribute_required():
    assert any('api_id' in i for i in mod.check(mutate('| api_id | api-vehicles-v1 |\n', '')))


def test_legacy_tc_without_contract_keeps_old_rules_only():
    legacy = EXAMPLE.replace('tc_contract: "1.4"\n', '')
    assert mod.is_legacy(legacy)
    assert mod.check(legacy) == []


def test_schema_enums_match_validator():
    enums = SCHEMA['frontmatter']['enums']
    assert set(enums['surface']) == mod.SURFACES
    assert set(enums['test_level']) == mod.TEST_LEVELS
    assert set(enums['test_type']) == mod.TEST_TYPES
    assert set(enums['priority']) == mod.PRIORITIES
    assert set(enums['criticality']) == mod.CRITICALITY
    assert set(enums['automation_status']) == mod.AUTOMATION
    assert SCHEMA['sections'] == mod.CONTRACT_SECTIONS
    assert SCHEMA['rules']['evidence_modes'] == list(mod.EVIDENCE_MODES)


def test_contract_copies_parse_and_declare_testcase_vocabulary():
    copies = sorted(SK.parent.glob('*/resources/contracts/common-contract.yaml'))
    assert len(copies) == 7
    for path in copies:
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        assert data['testcase_vocabulary']['test_level'], str(path)
        assert data['rules']['testcase_execution_neutral'] is True, str(path)


def test_api_tc_sin_api_id_en_frontmatter_falla():
    sin = EXAMPLE.replace("api_id: api-vehicles-v1\n", "")
    assert any("api_id obligatorio" in i for i in mod.check(sin))


def test_api_id_del_frontmatter_debe_coincidir_con_la_tabla():
    desalineado = EXAMPLE.replace("api_id: api-vehicles-v1\n", "api_id: otro-servicio\n")
    assert any("no coincide con el frontmatter" in i for i in mod.check(desalineado))


def test_tc_no_api_no_exige_api_id():
    no_api = EXAMPLE.replace("surface: API", "surface: WEB").replace("api_id: api-vehicles-v1\n", "")
    assert not any("api_id" in i for i in mod.check(no_api))
