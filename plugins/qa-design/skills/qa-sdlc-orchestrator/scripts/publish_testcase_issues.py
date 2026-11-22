#!/usr/bin/env python3
import os, json, sys, urllib.request, urllib.parse

def validate_case(tc):
    tid=tc.get("testcase_id","")
    if not tid.startswith("TC-"):
        raise ValueError("Only TC-* Test Cases can be published; TSN/other entities are forbidden")
    if tc.get("approved") is not True:
        raise ValueError(f"{tid}: only TC approved by TEST_DESIGN_REVIEW_GATE can be published (approved: true)")
    for k in ("testcase_title","scenario_refs","kb_local_path","kb_gitlab_url"):
        if not tc.get(k):
            raise ValueError(f"{tid}: {k} required")
    return tc

def check_approval(payload):
    ha=payload.get("human_approval") or {}
    if not (ha.get("approved") and ha.get("actor") and ha.get("evidence_ref") and ha.get("artifact_revision")):
        raise RuntimeError("human_approval (approved, actor, evidence_ref, artifact_revision) is required before publishing (TESTCASE_PUBLICATION_GATE is MANDATORY_HIL)")

def description(tc, issue_url=""):
    validate_case(tc)
    fields=["testcase_id","short_purpose","intent_summary","test_surface","test_level","test_type","priority","criticality","automation_status","scenario_refs","dsp_ref","requirement_refs","risk_refs","kb_local_path","kb_gitlab_url"]
    lines=[]
    for k in fields:
        v=tc.get(k,"")
        if isinstance(v,list): v=", ".join(v)
        lines.append(f"- {k}: {v}")
    lines.append(f"- issue_url_after_creation: {issue_url}")
    return "\n".join(lines)

def api(url, pat, method="GET", data=None):
    req=urllib.request.Request(url, method=method, headers={"PRIVATE-TOKEN":pat})
    if data is not None:
        payload=urllib.parse.urlencode(data).encode()
        req.data=payload
        req.add_header("Content-Type","application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def find_existing(base, project, pat, tid):
    q=urllib.parse.urlencode({"labels":"TestCase","scope":"all","search":tid,"per_page":100})
    items=api(f"{base}/api/v4/projects/{urllib.parse.quote(str(project),safe='')}/issues?{q}",pat)
    for i in items:
        if tid in (i.get("title","")+" "+i.get("description","")): return i
    return None

def publish(payload, dry_run=False):
    check_approval(payload)
    for raw in payload["test_cases"]:
        validate_case(raw)
    if dry_run:
        return {"project_id":payload["gitlab_id"],"dry_run":True,"issues":[{"title":f"[{t['testcase_id']}] {t['testcase_title']}","description":description(t)} for t in payload["test_cases"]]}
    pat=os.environ.get("GITLAB_PAT")
    if not pat: raise RuntimeError("GITLAB_PAT is required at runtime")
    base=payload["gitlab_url"].rstrip("/"); project=payload["gitlab_id"]; out=[]
    for raw in payload["test_cases"]:
        tc=validate_case(raw); tid=tc["testcase_id"]
        old=find_existing(base,project,pat,tid)
        if old:
            out.append({"testcase_id":tid,"status":"existing","iid":old["iid"],"web_url":old["web_url"]}); continue
        created=api(f"{base}/api/v4/projects/{urllib.parse.quote(str(project),safe='')}/issues",pat,"POST",
                    {"title":f"[{tid}] {tc['testcase_title']}","labels":"TestCase","description":description(tc)})
        final=api(f"{base}/api/v4/projects/{urllib.parse.quote(str(project),safe='')}/issues/{created['iid']}",pat,"PUT",
                  {"description":description(tc,created["web_url"])})
        out.append({"testcase_id":tid,"status":"created","iid":final["iid"],"web_url":final["web_url"]})
    return {"project_id":project,"results":out}

if __name__=="__main__":
    payload=json.load(open(sys.argv[1],encoding="utf-8"))
    print(json.dumps(publish(payload,dry_run="--dry-run" in sys.argv[2:]),indent=2,ensure_ascii=False))
