import unittest, tempfile, importlib.util, hashlib, json, re, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
WF_PATH=ROOT/"skills/infrastructure-orchestrator/scripts/workflow.py"
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
wf=load_module(WF_PATH,"wf")
BS=chr(92)+"n"
def frontmatter(path):
 m=re.match(r"\A---\n(.*?)\n---\n",Path(path).read_text(encoding="utf8"),re.S);return yaml.safe_load(m.group(1)) if m else None
def render(template,dest):
 dest.write_text(re.sub(r"\{\{ [a-z_]+ \}\}","x",template.read_text(encoding="utf8")),encoding="utf8");return dest
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class TestPlugin(unittest.TestCase):
 def test_structure(self):
  names=list((ROOT/"skills").iterdir());self.assertEqual(len(names),7)
  for p in names:
   for d in ("assets","templates","scripts","resources","examples"):self.assertTrue((p/d).is_dir())
   self.assertTrue((p/"SKILL.md").is_file())
 def test_modes(self):
  with tempfile.TemporaryDirectory() as d:
   for mode in ("greenfield","brownfield","evolution"):
    p=Path(d)/f"{mode}.json"
    wf.create(p,mode,[{"id":"T1","skill":"infrastructure-assessment"},{"id":"T2","skill":"infrastructure-architecture-design","depends_on":["T1"]}])
    with self.assertRaises(ValueError):wf.update(p,"T2","READY")
    wf.update(p,"T1","READY")
    wf.update(p,"T1","IN_PROGRESS",execution_id="x")
    wf.update(p,"T1","IN_REVIEW",execution_id="x")
    artifact=Path(d)/f"{mode}.md";artifact.write_text("evidence")
    e=[{"path":str(artifact),"sha256":hashlib.sha256(artifact.read_bytes()).hexdigest()}]
    with self.assertRaises(ValueError):wf.update(p,"T1","COMPLETED",execution_id="wrong",evidence=e)
    wf.update(p,"T1","COMPLETED",execution_id="x",evidence=e)
    wf.update(p,"T2","READY")
    self.assertEqual(wf.load(p)["tasks"]["T1"]["status"],"COMPLETED")
 def test_failure_and_gates(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"plan.json";wf.create(p,"evolution",[{"id":"T1"}],[{"id":"DESIGN_READY","after":[]}])
   wf.update(p,"T1","READY")
   wf.update(p,"T1","IN_PROGRESS",execution_id="y")
   with self.assertRaises(ValueError):wf.update(p,"T1","FAILED",execution_id="y")
   wf.update(p,"T1","FAILED",execution_id="y",reason="missing data")
   wf.update(p,"T1","READY")
   with self.assertRaises(ValueError):wf.approve_gate(p,"DESIGN_READY","","")
   wf.approve_gate(p,"DESIGN_READY","human:architect","MR-42")
   self.assertEqual(wf.load(p)["gates"]["DESIGN_READY"]["status"],"APPROVED")
 def test_templates(self):
  for p in (ROOT/"skills").iterdir():
   for t in p.glob("templates/*-okf.md"):
    s=t.read_text();self.assertIn("sources:",s);self.assertIn("generated:",s)
 def test_cycle(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):
    wf.create(Path(d)/"p.json","greenfield",[{"id":"A","depends_on":["B"]},{"id":"B","depends_on":["A"]}])
 def test_validate_accepts_rendered_templates(self):
  with tempfile.TemporaryDirectory() as d:
   for p in (ROOT/"skills").iterdir():
    v=load_module(p/"scripts/validate.py","v_"+p.name)
    for t in p.glob("templates/*-okf.md"):self.assertTrue(v.validate(render(t,Path(d)/t.name)))
 def test_validate_rejects_bad_artifacts(self):
  v=load_module(ROOT/"skills/infrastructure-orchestrator/scripts/validate.py","v")
  with tempfile.TemporaryDirectory() as d:
   t=ROOT/"skills/infrastructure-architecture-design/templates/topology-okf.md"
   ok=render(t,Path(d)/"ok.md")
   with self.assertRaises(ValueError):v.validate(t)
   (Path(d)/"nofm.md").write_text("# no frontmatter\n");self.assertRaises(ValueError,v.validate,Path(d)/"nofm.md")
   (Path(d)/"nostatus.md").write_text(ok.read_text(encoding="utf8").replace("status: draft\n",""),encoding="utf8");self.assertRaises(ValueError,v.validate,Path(d)/"nostatus.md")
   (Path(d)/"crlf.md").write_bytes(ok.read_text(encoding="utf8").replace("\n","\r\n").encode());self.assertTrue(v.validate(Path(d)/"crlf.md"))
 def test_events_log_is_jsonl(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"plan.json";wf.create(p,"greenfield",[{"id":"T1"}])
   wf.update(p,"T1","READY");wf.update(p,"T1","IN_PROGRESS",execution_id="x")
   lines=Path(str(p)+".events.jsonl").read_text().splitlines()
   self.assertEqual(len(lines),2);self.assertEqual([json.loads(l)["to"] for l in lines],["READY","IN_PROGRESS"])
 def test_default_graph_per_mode(self):
  with tempfile.TemporaryDirectory() as d:
   for mode in wf.MODES:
    plan=wf.create(Path(d)/f"{mode}.json",mode)
    self.assertEqual(len(plan["tasks"]),6);self.assertEqual(len(plan["gates"]),5)
    self.assertEqual(plan["tasks"]["T5_delivery"]["depends_on"],["T3_security","T4_operations"])
    self.assertEqual({plan["tasks"][t]["skill"] for t in plan["tasks"]},wf.SPECIALISTS)
 def test_unknown_skill_and_gate_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertRaises(ValueError,wf.create,Path(d)/"a.json","greenfield",[{"id":"T1","skill":"nope"}])
   self.assertRaises(ValueError,wf.create,Path(d)/"b.json","greenfield",[{"id":"T1","requires_gates":["G"]}])
 def test_gates_are_enforced(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"plan.json";wf.create(p,"greenfield")
   art=Path(d)/"a.md";art.write_text("evidence");ev=[{"path":str(art),"sha256":sha(art)}]
   self.assertEqual(wf.refresh(p),["T1_assessment"])
   with self.assertRaises(ValueError):wf.approve_gate(p,"G1_BASELINE_APPROVED","human:architect","MR-1")
   wf.update(p,"T1_assessment","IN_PROGRESS",execution_id="x");wf.update(p,"T1_assessment","IN_REVIEW",execution_id="x")
   wf.update(p,"T1_assessment","COMPLETED",execution_id="x",evidence=ev)
   with self.assertRaises(ValueError):wf.update(p,"T2_architecture","READY")
   self.assertEqual(wf.refresh(p),[])
   with self.assertRaises(ValueError):wf.approve_gate(p,"G1_BASELINE_APPROVED","agent:claude","MR-1")
   with self.assertRaises(ValueError):wf.approve_gate(p,"NO_SUCH_GATE","human:architect","MR-1")
   wf.approve_gate(p,"G1_BASELINE_APPROVED","human:architect","MR-1")
   self.assertEqual(wf.refresh(p),["T2_architecture"]);self.assertEqual(wf.ready(p),["T2_architecture"])
 def test_submit_result_aligned_with_state_machine(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"plan.json";wf.create(p,"greenfield");wf.refresh(p)
   wf.update(p,"T1_assessment","IN_PROGRESS",execution_id="x")
   art=Path(d)/"baseline.md";art.write_text("evidence")
   r=Path(d)/"task-result.yaml"
   def write(**kw):
    base=dict(task_id="T1_assessment",execution_id="x",skill="infrastructure-assessment",status="IN_REVIEW",artifacts=[{"path":str(art),"sha256":sha(art)}],evidence=[],errors=[])
    r.write_text(yaml.safe_dump(dict(base,**kw)))
   write(status="COMPLETED");self.assertRaises(ValueError,wf.submit_result,p,r)
   write(skill="infrastructure-security-design");self.assertRaises(ValueError,wf.submit_result,p,r)
   write(artifacts=[{"path":str(art),"sha256":"0"*64}]);self.assertRaises(ValueError,wf.submit_result,p,r)
   write();wf.submit_result(p,r);self.assertEqual(wf.load(p)["tasks"]["T1_assessment"]["status"],"IN_REVIEW")
   self.assertEqual(wf.load(p)["tasks"]["T1_assessment"]["submitted"]["artifacts"][0]["sha256"],sha(art))
 def test_cli_smoke(self):
  with tempfile.TemporaryDirectory() as d:
   run=lambda *a:subprocess.run([sys.executable,"-B",str(WF_PATH),*a],capture_output=True,text=True)
   r=["--root",d,"--run-id","run-1"]
   self.assertEqual(run("create",*r,"--mode","greenfield").returncode,0)
   self.assertIn("T1_assessment",run("refresh",*r).stdout)
   self.assertIn("READY",run("status",*r).stdout)
   bad=run("approve-gate",*r,"--gate","G1_BASELINE_APPROVED","--actor","agent:x","--evidence","MR-1")
   self.assertEqual(bad.returncode,1);self.assertIn("ERROR",bad.stderr)
 def test_operational_files_live_under_comsatel(self):
  with tempfile.TemporaryDirectory() as d:
   run=lambda *a:subprocess.run([sys.executable,"-B",str(WF_PATH),*a],capture_output=True,text=True)
   r=["--root",d,"--run-id","run-1"];base=Path(d)/".comsatel"/"infra-architecture-design"/"runs"/"run-1"
   self.assertEqual(run("create",*r,"--mode","greenfield").returncode,0)
   run("refresh",*r)
   self.assertTrue((base/"plan.json").is_file());self.assertTrue((base/"plan.json.events.jsonl").is_file())
   self.assertEqual([p.name for p in Path(d).iterdir()],[".comsatel"])
   out=run("create","--plan",str(Path(d)/"plan.json"),"--mode","greenfield")
   self.assertEqual(out.returncode,1);self.assertIn("comsatel",out.stderr);self.assertFalse((Path(d)/"plan.json").exists())
   self.assertEqual(run("status","--root",d).returncode,1)
   (Path(d)/"task-result.yaml").write_text("task_id: T1_assessment\n")
   bad=run("submit-result",*r,"--result",str(Path(d)/"task-result.yaml"))
   self.assertEqual(bad.returncode,1);self.assertIn("run folder",bad.stderr)
 def test_pathmap_is_single_source_under_comsatel(self):
  pm=json.loads((ROOT/"assets/pathmap.json").read_text())
  self.assertEqual(pm["orchestrator_root"],".comsatel/infra-architecture-design/runs/")
  self.assertEqual(sorted(pm["document_types"]),sorted(pm["artifacts"]))
  for v in pm["document_types"].values():self.assertTrue(v.startswith(pm["output_root"]+"/"),v)
  self.assertEqual(list(ROOT.glob("skills/*/assets/pathmap.json")),[])
 def test_pathmap_okf_types_match_templates_and_catalogs(self):
  # D-15: okf_types documenta la equivalencia slug -> código OKF; debe coincidir con catálogos y plantillas
  pm=json.loads((ROOT/"assets/pathmap.json").read_text(encoding="utf8"));ok=pm["okf_types"]
  cat={}
  for p in (ROOT/"skills").iterdir():
   cat.update(yaml.safe_load((p/"assets/artifact-catalog.yaml").read_text(encoding="utf8"))["types"])
  self.assertEqual(ok,{k:cat[k] for k in ok});self.assertEqual(sorted(ok),sorted(cat))
  for k in pm["document_types"]:self.assertIn(k,ok)
 def test_documentacion_sin_rutas_con_barras_invertidas(self):
  txt=(ROOT/"skills/infrastructure-orchestrator/SKILL.md").read_text(encoding="utf8")
  self.assertNotIn(chr(92)+"comsatel",txt);self.assertIn(".comsatel/infra-architecture-design/runs/<run-id>/",txt)
  self.assertIn("v"+json.loads((ROOT/".claude-plugin/plugin.json").read_text())["version"],(ROOT/"README.md").read_text(encoding="utf8").splitlines()[0])
 def test_plugin_files_parse(self):
  for rel in ("commands/infrastructure-plan.md","agents/infrastructure-architect.md"):
   fm=frontmatter(ROOT/rel);self.assertIsInstance(fm,dict,rel);self.assertTrue(fm.get("description"),rel)
  self.assertEqual(frontmatter(ROOT/"agents/infrastructure-architect.md")["name"],"infrastructure-architect")
  for p in (ROOT/"skills").iterdir():
   fm=frontmatter(p/"SKILL.md");self.assertEqual(fm["name"],p.name);self.assertTrue(fm["description"])
 def test_no_literal_backslash_n_in_text_files(self):
  for f in ROOT.rglob("*"):
   if f.is_file() and f.suffix in (".md",".yaml",".json") and "standards" not in f.parts:
    self.assertNotIn(BS,f.read_text(encoding="utf8"),str(f.relative_to(ROOT)))
 def test_descriptions_route_to_orchestrator(self):
  orch=frontmatter(ROOT/"skills/infrastructure-orchestrator/SKILL.md")["description"]
  self.assertNotIn("assigns a contract-bound task",orch);self.assertIn("Use when the user asks",orch)
  for p in (ROOT/"skills").iterdir():
   if p.name!="infrastructure-orchestrator":self.assertIn("dispatched by infrastructure-orchestrator",frontmatter(p/"SKILL.md")["description"])
 def test_result_contract_matches_state_machine(self):
  sm=yaml.safe_load((ROOT/"skills/infrastructure-orchestrator/resources/state-machine.yaml").read_text())
  for p in (ROOT/"skills").iterdir():
   oc=yaml.safe_load((p/"resources/output-contract.yaml").read_text())
   self.assertEqual(oc["result_status_values"],sm["specialist_result_statuses"]);self.assertNotIn("COMPLETED",oc["result_status_values"])
   self.assertTrue(set(sm["specialist_result_statuses"])<=set(sm["states"]))
 def test_types_and_sections(self):
  v=load_module(ROOT/"skills/infrastructure-orchestrator/scripts/validate.py","vt")
  with tempfile.TemporaryDirectory() as d:
   cat={}
   for p in (ROOT/"skills").iterdir():
    c=yaml.safe_load((p/"assets/artifact-catalog.yaml").read_text(encoding="utf8"))
    self.assertEqual(sorted(c["artifacts"]),sorted(c["types"]))
    for a,sg in c["types"].items():
     t=p/f"templates/{a}-okf.md";self.assertEqual(frontmatter(t)["type"],sg);cat[a]=sg
   self.assertEqual(len(cat),22);self.assertNotIn("DOC",cat.values())
   t=ROOT/"skills/infrastructure-architecture-design/templates/topology-okf.md"
   ok=render(t,Path(d)/"ok.md")
   (Path(d)/"doc.md").write_text(ok.read_text(encoding="utf8").replace("type: ITP","type: DOC"),encoding="utf8");self.assertRaises(ValueError,v.validate,Path(d)/"doc.md")
   (Path(d)/"sec.md").write_text(ok.read_text(encoding="utf8").replace("## Alcance","## Otro"),encoding="utf8");self.assertRaises(ValueError,v.validate,Path(d)/"sec.md")
if __name__=="__main__":unittest.main()
