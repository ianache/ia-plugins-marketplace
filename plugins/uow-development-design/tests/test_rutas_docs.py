import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_documentacion_usa_la_ruta_con_punto():
    # D-18: la documentación cita .comsatel/uow-development-design/runs/ como el pathmap y el orquestador
    for f in [ROOT / 'README.md', ROOT / 'DOCUMENTACION.md'] + list(ROOT.glob('skills/*/SKILL.md')):
        assert not re.search(r'(^|[^.\w/])comsatel/uow-development-design', f.read_text(encoding='utf-8')), f
