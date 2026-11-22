import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
APROBADOS = {'UXR', 'FLW', 'SCR', 'CMP', 'TKN', 'HOF', 'WEB', 'MOB'}


def test_plantillas_usan_tipo_aprobado_sin_marcas_de_provisional():
    # D-11: UXR/FLW/SCR/CMP/TKN/HOF/WEB/MOB están aprobados en STD-OKF-001 v0.1.0-stable
    plantillas = list(ROOT.glob('skills/*/templates/deliverable*.md'))
    assert plantillas
    for f in plantillas:
        linea = next(l for l in f.read_text(encoding='utf-8').splitlines() if l.startswith('type:'))
        assert linea.split('#')[0].split(':')[1].strip() in APROBADOS, f
        assert not re.search(r'(?i)propuest|provisional', linea), f


def test_textos_no_describen_los_tipos_como_provisionales():
    for f in list(ROOT.glob('README.md')) + list(ROOT.glob('skills/*/SKILL.md')):
        assert not re.search(r'(?i)(WEB|MOB|UXR)`? (sigue |es )?(provisional|\*\*propuesta)', f.read_text(encoding='utf-8')), f
