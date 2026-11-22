import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_documentacion_usa_la_ruta_con_punto_y_la_version_vigente():
    # D-17: README/VALIDATION/SKILL coinciden con workflow.py (.comsatel/project-management/runs/) y plugin.json
    import json
    ver = json.loads((ROOT / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    assert f'v{ver}' in (ROOT / 'README.md').read_text(encoding='utf-8').splitlines()[0]
    assert f'v{ver}' in (ROOT / 'VALIDATION.md').read_text(encoding='utf-8').splitlines()[0]
    docs = [ROOT / 'README.md', ROOT / 'VALIDATION.md'] + list(ROOT.glob('skills/*/SKILL.md')) + list(ROOT.glob('skills/*/references/*.md'))
    for f in docs:
        assert not re.search(r'(^|[^.\w/])comsatel/', f.read_text(encoding='utf-8')), f
