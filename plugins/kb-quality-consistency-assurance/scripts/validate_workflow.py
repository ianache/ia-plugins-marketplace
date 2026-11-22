#!/usr/bin/env python3
"""Validate KB-QCA workflow DAG; JSON input uses the same schema as YAML plan."""
import json, sys
from pathlib import Path

def validate(plan):
    errors=[]
    nodes=plan.get('nodes', [])
    ids=[n.get('id') for n in nodes]
    if len(ids)!=len(set(ids)): errors.append('duplicate node id')
    by_id={n.get('id'):n for n in nodes}
    for n in nodes:
        nid=n.get('id')
        if n.get('kind') not in ('task','gate'):errors.append(f'{nid}: invalid kind')
        for dep in n.get('depends_on',[]):
            if dep not in by_id:errors.append(f'{nid}: missing dependency {dep}')
        if n.get('kind')=='gate':
            for producer in n.get('evaluates',[]):
                if producer not in by_id:errors.append(f'{nid}: unknown producer {producer}')
                elif by_id[producer].get('kind')!='task':errors.append(f'{nid}: producer must be task: {producer}')
                elif producer not in n.get('depends_on',[]):
                    # indirect dependency also permitted
                    def reaches(start, target, seen=None):
                        seen=set() if seen is None else seen
                        if start==target:return True
                        if start in seen:return False
                        seen.add(start)
                        return any(reaches(d,target,seen.copy()) for d in by_id.get(start,{}).get('depends_on',[]))
                    if not reaches(nid,producer):errors.append(f'{nid}: gate does not follow producer {producer}')
    state={}
    def visit(nid,stack):
        if state.get(nid)==1:
            errors.append('dependency cycle: '+' -> '.join(stack+[nid]));return
        if state.get(nid)==2:return
        state[nid]=1
        for dep in by_id[nid].get('depends_on',[]):
            if dep in by_id:visit(dep,stack+[nid])
        state[nid]=2
    for nid in by_id:visit(nid,[])
    return list(dict.fromkeys(errors))

def main():
    if len(sys.argv)!=2:
        print('Usage: validate_workflow.py plan.json (JSON equivalent of run-plan.yaml)',file=sys.stderr);return 2
    errors=validate(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps({'valid':not errors,'errors':errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
