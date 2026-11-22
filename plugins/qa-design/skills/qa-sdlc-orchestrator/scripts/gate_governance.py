"""Deterministic gate policy decisions; does not dispatch agents or grant human approval."""
MODES={'AUTO','CONDITIONAL_HIL','MANDATORY_HIL'}
def decide(policy,checks,attempts=0,human_approval=None):
 mode=policy['mode']
 if mode not in MODES: raise ValueError('Unknown gate policy')
 if not isinstance(checks,list) or not checks: raise ValueError('Checks required')
 if any(c.get('result') not in ('PASS','FAIL','UNCERTAIN') for c in checks):raise ValueError('Invalid check result')
 if any(c.get('evidence_ref') is None for c in checks):raise ValueError('Evidence references required')
 if any(c.get('result')=='UNCERTAIN' for c in checks):return {'gate_status':'BLOCKED','action':'REQUEST_HIL','reason':'uncertain_evidence'}
 if any(c.get('result')=='FAIL' and c.get('requires_hil',False) for c in checks):return {'gate_status':'BLOCKED','action':'REQUEST_HIL','reason':'high_risk_trigger'}
 if any(c['result']=='FAIL' for c in checks):
  if attempts < policy.get('max_retries',0):return {'gate_status':'FAIL','action':'AUTO_RETRY','reason':'check_failed'}
  return {'gate_status':'BLOCKED','action':'REQUEST_HIL','reason':'retries_exhausted'}
 if mode=='MANDATORY_HIL':
  if not human_approval or not human_approval.get('approved') or not human_approval.get('actor') or not human_approval.get('evidence_ref') or not human_approval.get('artifact_revision'):
   return {'gate_status':'BLOCKED','action':'REQUEST_HIL','reason':'approval_required'}
  if human_approval['artifact_revision'] != policy.get('artifact_revision'):
   return {'gate_status':'BLOCKED','action':'REQUEST_HIL','reason':'approval_stale'}
 return {'gate_status':'PASS','action':'AUTO_ADVANCE','reason':'verified'}
