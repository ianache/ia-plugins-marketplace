import pytest
import json, subprocess, sys, tempfile, pathlib, yaml
ROOT=pathlib.Path(__file__).resolve().parents[1]
import re
version=json.loads((ROOT/'.claude-plugin/plugin.json').read_text(encoding='utf-8'))['version']
assert re.fullmatch(r'\d+\.\d+\.\d+',version),version
# la versión vigente (plugin.json) debe ser la última publicada en el CHANGELOG; así la prueba no se rompe en cada versión nueva
latest=re.search(r'(?m)^## \[(\d+\.\d+\.\d+)\]',(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')).group(1)
assert version==latest,(version,latest)
assert len(list((ROOT/'skills').glob('*/SKILL.md')))==7


def _filled_handoff(scenario):
    # Una plantilla no es un artefacto: el test la rellena con valores válidos de ejemplo.
    import yaml as _yaml
    return _yaml.safe_dump({'handoff': {
        'service_id': 'tracking-svc', 'scenario': scenario,
        'knowledge_base': {'target': 'codebase/tracking-svc', 'design_ref': 'CL2-BC-001'},
        'source_repository': {'project': 'cl2/tracking-svc', 'target_branch': 'develop', 'source_ref': 'refs/heads/develop',
                              'source_commit': 'a' * 40},
        'architecture': {'adr_refs': ['ADR-014']},
        'artifacts': [{'id': 'API-TRACKING', 'source': 'to-be/api-integration-design.md', 'target': 'src/main/resources/api/api.yaml',
                       'action': 'update', 'validation': 'openapi-lint-and-compatibility'}],
        'controls': {'require_human_approval': True, 'publish_via_merge_request': True,
                     'require_adr_compliance': True, 'require_backward_compatibility': True}}})

@pytest.mark.parametrize("scenario", ["greenfield", "brownfield", "evolution"])
def test_workflow_scenario(scenario):
    with tempfile.TemporaryDirectory() as tmp:
      cmd=[sys.executable,str(ROOT/'scripts/workflow.py')]
      def call(*args):
        p=subprocess.run([*cmd,*map(str,args)],capture_output=True,text=True)
        return p
    
      ws=pathlib.Path(tmp)/scenario; run=ws/'.comsatel'/'microservice-api-design'/'runs'/'test'
      (ws/'codebase'/'tracking-svc').mkdir(parents=True)
      assert call('init',run,'--scope','DSP-001','--scenario',scenario,'--service','tracking-svc','--workspace-root',ws).returncode==0
      assert call('check',run).returncode==0
      assert call('approve-gate',run,'--gate','G0','--actor','human:test','--evidence','MR-1').returncode!=0
      manifest=yaml.safe_load((run/'scope-manifest.yaml').read_text());manifest['sources']=['DSP-001'];manifest['missing_sources']=[]
      (run/'scope-manifest.yaml').write_text(yaml.safe_dump(manifest))
      assert call('approve-gate',run,'--gate','G0','--actor','human:test','--evidence','MR-1').returncode==0
      plan=yaml.safe_load((run/'execution-plan.yaml').read_text())
      for gate, nextgate in [('G0','G1'),('G1','G2'),('G2','G3'),('G3','G4')]:
        for task in [t for t in plan['tasks'] if t['gate']==gate]:
          for state in ('READY','IN_PROGRESS'):
            r=call('transition',run,'--task',task['id'],'--to',state,'--actor','agent:test','--reason','test')
            assert r.returncode==0,r.stderr
          for output in task['outputs']:
            f=pathlib.Path(output);f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text(_filled_handoff(scenario) if output.endswith('codebase-handoff.yaml') else (ROOT/'templates/fdt-manifest.yaml').read_text() if output.endswith('fdt-manifest.yaml') else 'test evidence')
            if output.endswith('fdt-manifest.yaml'):(f.parent/'CL2-FDT-001-registrar-distribuidor.md').write_text((ROOT/'templates/fdt-functionality.md').read_text())
          for state in ('NEEDS_REVIEW','DONE'):
            r=call('transition',run,'--task',task['id'],'--to',state,'--actor','human:test','--reason','reviewed','--evidence','review-1')
            assert r.returncode==0,r.stderr
        r=call('approve-gate',run,'--gate',nextgate,'--actor','human:test','--evidence','MR-1')
        assert r.returncode==0,r.stderr
      assert call('status',run).returncode==0


def test_init_fallido_es_atomico():
    # D-02: un init que falla por falta de codebase/<servicio> no deja carpeta; el reintento con el mismo run-id funciona
    with tempfile.TemporaryDirectory() as tmp:
        ws=pathlib.Path(tmp); run=ws/'.comsatel'/'microservice-api-design'/'runs'/'RUN-X'
        args=[sys.executable,str(ROOT/'scripts/workflow.py'),'init',str(run),'--scope','DSP-001','--scenario','greenfield','--service','svc','--workspace-root',str(ws)]
        p=subprocess.run(args,capture_output=True,text=True)
        assert p.returncode!=0 and 'codebase/svc' in (p.stdout+p.stderr)
        assert not run.exists() and not (ws/'design').exists()
        (ws/'codebase'/'svc').mkdir(parents=True)
        p=subprocess.run(args,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert (run/'execution-plan.yaml').exists()


def test_rutas_documentadas_coinciden_con_el_plan():
    # D-03: la tabla 3.2 de DOCUMENTACION debe coincidir con output_path de cada tarea; ningún SKILL conserva el artefacto de plantilla
    doc=(ROOT/'DOCUMENTACION.md').read_text(encoding='utf-8')
    tabla=set(re.findall(r'^\| `([\w\-/]+\.(?:md|yaml))`',doc.split('### 3.2')[1].split('###')[0],re.M))
    for f in (ROOT/'skills').glob('*/SKILL.md'):
        assert '(ruta exacta' not in f.read_text(encoding='utf-8'),f
    with tempfile.TemporaryDirectory() as tmp:
        ws=pathlib.Path(tmp); (ws/'codebase'/'svc').mkdir(parents=True); run=ws/'.comsatel'/'microservice-api-design'/'runs'/'R'
        p=subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),'init',str(run),'--scope','D','--scenario','evolution','--service','svc','--workspace-root',str(ws)],capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        plan=yaml.safe_load((run/'execution-plan.yaml').read_text())
        base=(ws/'design'/'microservices'/'svc').resolve(); docs=(ws/'codebase'/'svc'/'docs').resolve()
        for t in plan['tasks']:
            out=pathlib.Path(t['output_path']).resolve()
            rel=out.relative_to(docs).as_posix() if t['document_type']=='C4' else out.relative_to(base).as_posix()
            assert rel in tabla,(rel,tabla)
        # D-10: EVT y C4 tienen tarea propia en los tres escenarios
        for sc in ('greenfield','brownfield','evolution'):
            r2=ws/'.comsatel'/'microservice-api-design'/'runs'/sc
            assert subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),'init',str(r2),'--scope','D','--scenario',sc,'--service','svc','--workspace-root',str(ws)],capture_output=True,text=True).returncode==0
            tipos={t['document_type'] for t in yaml.safe_load((r2/'execution-plan.yaml').read_text())['tasks']}
            assert {'EVT','C4'}<=tipos,(sc,tipos)


def test_approve_gate_exige_prefijo_human():
    # D-07: --actor sin prefijo human: se rechaza
    with tempfile.TemporaryDirectory() as tmp:
        ws=pathlib.Path(tmp); (ws/'codebase'/'svc').mkdir(parents=True); run=ws/'.comsatel'/'microservice-api-design'/'runs'/'R'
        base=[sys.executable,str(ROOT/'scripts/workflow.py')]
        assert subprocess.run([*base,'init',str(run),'--scope','D','--scenario','greenfield','--service','svc','--workspace-root',str(ws)],capture_output=True,text=True).returncode==0
        p=subprocess.run([*base,'approve-gate',str(run),'--gate','G0','--actor','reviewer','--evidence','MR-1'],capture_output=True,text=True)
        assert p.returncode!=0 and 'human:' in (p.stdout+p.stderr)
