import pathlib, re, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
WF = str(ROOT / 'scripts' / 'workflow.py')


def _bloque_cli(texto):
    m = re.search(r'```bash\n(python scripts/workflow\.py init.*?)```', texto, re.S)
    assert m, 'README sin bloque CLI'
    return [l for l in m.group(1).splitlines() if l.startswith('python scripts/workflow.py')]


def _ejecuta(cmd, cwd):
    args = cmd.replace('python scripts/workflow.py', '').split()
    return subprocess.run([sys.executable, WF, *args], cwd=cwd, capture_output=True, text=True)


def test_init_y_check_documentados_funcionan_en_carpeta_vacia():
    # D-01: copiar y pegar init + check del README en un workspace vacío debe funcionar
    cmds = _bloque_cli((ROOT / 'README.md').read_text(encoding='utf-8'))
    init = next(c for c in cmds if ' init ' in c)
    check = next(c for c in cmds if ' check ' in c)
    with tempfile.TemporaryDirectory() as tmp:
        for c in (init, check):
            p = _ejecuta(c, tmp)
            assert p.returncode == 0, (c, p.stdout, p.stderr)


def test_documentacion_usa_ruta_con_punto():
    for f in ('README.md', 'DOCUMENTACION.md', 'skills/ddd-design-orchestrator/SKILL.md'):
        t = (ROOT / f).read_text(encoding='utf-8')
        assert not re.search(r'(^|[^.\w])comsatel/ddd-domain-design/runs', t), f


def test_approve_gate_exige_prefijo_human():
    # D-07: la aprobación de gates exige --actor human:<nombre>
    with tempfile.TemporaryDirectory() as tmp:
        run = '.comsatel/ddd-domain-design/runs/RUN-001'
        assert _ejecuta(f'python scripts/workflow.py init {run} --scope DSP-001 --workspace .', tmp).returncode == 0
        malo = _ejecuta(f"python scripts/workflow.py approve-gate {run} --gate G0 --actor reviewer --evidence MR-1", tmp)
        assert malo.returncode != 0 and 'human:' in (malo.stdout + malo.stderr)


def test_documenta_que_el_plugin_no_tiene_escenarios():
    # D-22: init no recibe --scenario; la reconstrucción As-Is la aporta microservice-api-design (ASIS)
    p = _ejecuta('python scripts/workflow.py init --help', '.')
    assert '--scenario' not in p.stdout
    for f in ('README.md', 'DOCUMENTACION.md', 'skills/ddd-design-orchestrator/SKILL.md'):
        t = (ROOT / f).read_text(encoding='utf-8')
        assert 'se usa igual en Greenfield, Brownfield y Evolution' in t and 'ASIS' in t, f
