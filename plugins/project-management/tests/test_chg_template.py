import pathlib, re
import yaml
ROOT = pathlib.Path(__file__).resolve().parents[1]
TPL = ROOT / 'skills/mgt-risk-change-controller/templates/change-request.md'


def front():
    return yaml.safe_load(re.match(r'\A---\n(.*?)\n---', TPL.read_text(encoding='utf-8'), re.S).group(1))


def test_chg_tiene_approved_by_y_estado_de_cambio_aparte_del_status():
    # D-27a: la decisión se registra en change_state/approved_by; status queda dentro del perfil de la KB
    m = front()
    assert m['status'] in ('draft', 'stable', 'deprecated')
    assert m['change_state'] == 'proposed'
    assert 'approved_by' in m and m['approved_by'] is None
