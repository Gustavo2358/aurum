#!/usr/bin/env python3
"""Build rule/support maps from the Clang AST and independently authored selections.
Selections identify causal support; AST extraction proves location, not semantics.
"""
import hashlib
import json
import re
from pathlib import Path
import subprocess
from clang import cindex
from gherkin.parser import Parser
from gherkin.pickles.compiler import Compiler
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evaluation'
RULES=json.loads((ROOT/'docs/oracle/rules.json').read_text())['rules']
# Each row is a reviewed support selection for one rule in catalog order.
SUPPORT={
'MNY':[
'money_valid','money_add money_valid','money_sub money_valid','floor_rate checked_mul',
'ceil_rate checked_mul','money_fx checked_mul','config_valid floor_rate money_fx','checked_mul'],
'PRC':[
'quote money_fx','quote money_fx','quote','price_components floor_rate','price_components',
'price_components checked_mul','price_components','execute quote'],
'ELG':[
'eligibility','eligibility','eligibility','eligibility','eligibility','eligibility','eligibility',
'eligibility','eligibility invoice_outstanding lot_principal lot_fee'],
'LIM':[
'available_credit project_account authorization_hold lot_principal lot_fee',
'credit_admission money_add authorize_apply','operation_admission authorize_apply quote',
'daily_admission daily_totals authorize_apply','count_admission daily_totals authorize_apply',
'daily_totals record_decision','daily_totals record_decision cancel_apply tick_apply refund_apply','authorize_apply record_decision daily_totals'],
'RSK':[
'risk_score','risk_score','risk_score','risk_score','recent_count risk_score authorize_apply',
'risk_classify','risk_score','risk_score'],
'AUT':[
'execute authorize_apply eligibility quote credit_admission risk_classify',
'authorize_apply authorization_hold ledger_pair project_account',
'authorize_apply project_account capture_apply',
'authorize_apply execute cacheable',
'authorize_apply risk_classify record_decision daily_totals recent_count',
'authorize_apply','authorize_apply quote price_components capture_apply',
'execute authorize_apply engine_clone array_append ledger_pair'],
'IDM':[
'execute command_same_key command_equal','execute command_same_key command_equal','command_equal parse_command command_default decimal_parse',
'execute command_same_key','cacheable execute','execute cacheable','execute capture_apply',
'execute cacheable'],
'CAP':[
'capture_admission capture_apply','capture_admission capture_apply money_sub',
'capture_apply cumulative_delta proportional','capture_state capture_apply authorization_hold',
'capture_apply ledger_pair project_account authorization_hold',
'capture_apply ledger_pair ledger_post ledger_balanced',
'capture_apply execute engine_clone array_append','capture_apply capture_admission'],
'REV':[
'cancel_apply authorization_hold ledger_pair',
'cancel_apply authorization_hold project_account',
'cancel_apply execute','tick_apply authorization_hold ledger_pair',
'refund_admission refund_apply','refund_apply cumulative_delta proportional',
'refund_apply refund_lot_order lot_principal lot_fee',
'refund_apply refund_post ledger_pair project_account',
'refund_apply daily_totals authorization_hold',
'refund_apply invoice_outstanding project_account'],
'INS':[
'installment_allowed capture_installment_allowed quote',
'installment_allowed','capture_installment_allowed installment_allowed',
'split_part capture_apply','split_part capture_apply',
'capture_apply invoice_due_day','split_part capture_apply','capture_installment_allowed capture_apply'],
'BIL':[
'close_admission close_apply','close_apply close_admission',
'close_apply','close_apply invoice_minimum',
'invoice_due_day close_apply','invoice_minimum ceil_rate',
'pay_apply allocate_late allocate_lots invoice_order lot_order',
'pay_apply allocate_lots project_account','payment_admission pay_apply execute',
'pay_apply allocate_lots invoice_outstanding eligibility',
'assess_apply invoice_outstanding ledger_pair','assess_apply invoice_outstanding'],
'REW':[
'reward_raw capture_apply','reward_raw capture_apply','reward_raw',
'reward_grant capture_apply','reward_gross capture_apply',
'refund_apply cumulative_delta proportional','refund_apply reward_gross reward_grant',
'reward_raw capture_apply'],
'BAT':[
'main execute','main execute engine_clone','execute command_equal',
'project_account daily_totals recent_count pay_apply',
'reconcile project_account authorization_hold lot_principal lot_fee',
'ledger_balanced ledger_pair ledger_post','write_auth_ids write_account write_result','tick_apply execute engine_clone'],
'IO':[
'parse_command command_valid command_field tokenize required_fields','parse_command tokenize','parse_command allowed_fields command_field','identifier_valid bounded_id',
'decimal_parse','read_line main','parse_command main','write_result main',
'main seed_load','seed_load seed_config seed_account seed_card seed_merchant config_valid','array_append execute engine_clone','main execute']}

CONTRACTS={
'money.c':['docs/contracts/INPUT_SCHEMA.md','docs/DOMAIN.md'],
'policy.c':['docs/DOMAIN.md','docs/contracts/OPERATIONS.md'],
'lifecycle.c':['docs/contracts/OPERATIONS.md','docs/contracts/STATE_AND_LEDGER.md'],
'billing.c':['docs/contracts/OPERATIONS.md','docs/contracts/STATE_AND_LEDGER.md'],
'state.c':['docs/contracts/STATE_AND_LEDGER.md','docs/ARCHITECTURE.md'],
'engine.c':['docs/contracts/OPERATIONS.md','docs/contracts/STATE_AND_LEDGER.md'],
'protocol.c':['docs/contracts/INPUT_SCHEMA.md','docs/contracts/IO_AND_HARNESS.md'],
'output.c':['docs/contracts/IO_AND_HARNESS.md','docs/contracts/INPUT_SCHEMA.md'],
'main.c':['docs/contracts/IO_AND_HARNESS.md']}
# Specific guards inside shared functions narrow the reverse map where their predicate is decisive.
REGIONS={
'risk_score': [('country','BR-RSK-002'),('present','BR-RSK-003'),('p >=','BR-RSK-004'),('recent','BR-RSK-005'),('score <','BR-RSK-007')],
'eligibility': [('a->active','BR-ELG-001'),('card->active','BR-ELG-002'),('expiry_day','BR-ELG-003'),('m->active','BR-ELG-004'),('m->category','BR-ELG-005'),('allow_international','BR-ELG-006'),('allow_contactless','BR-ELG-007'),('pin_ok','BR-ELG-008'),('invoices_len','BR-ELG-009'),('due_day','BR-ELG-009')],
'price_components':[('currency','BR-PRC-004 BR-PRC-005'),('tier','BR-PRC-005'),('installment_bps','BR-PRC-006'),('tariff_cap','BR-PRC-007')],
'quote':[('currency','BR-PRC-001 BR-PRC-002 BR-PRC-003'),('money_fx','BR-PRC-002 BR-MNY-006'),('installment_allowed','BR-INS-001 BR-INS-002 BR-INS-003')],
'execute':[('command_valid','FR-IO-001'),('QUOTE','BR-PRC-008 BR-IDM-008'),('GET_','BR-IDM-008'),('RECONCILE','BR-BAT-005'),('keys_len','BR-IDM-001 BR-IDM-004'),('key->command','BR-IDM-001 BR-IDM-002 BR-IDM-004'),('command_equal','BR-IDM-001 BR-IDM-002 BR-IDM-003'),('engine_clone','BR-AUT-008 BR-CAP-007 FR-IO-011'),('cacheable','BR-IDM-005 BR-IDM-006'),('array_append','FR-IO-011 BR-AUT-008'),('refresh_projections','BR-BAT-005 BR-MNY-002'),('r.decision==ERROR','BR-AUT-004 BR-CAP-007 BR-BAT-008')],
'capture_apply':[('capture_admission','BR-CAP-001 BR-CAP-002'),('capture_installment','BR-INS-008'),('cumulative_delta','BR-CAP-003'),('index <','BR-INS-004 BR-INS-005 BR-INS-006 BR-INS-007'),('ledger_pair','BR-CAP-005 BR-CAP-006'),('array_append','BR-CAP-007 FR-IO-011')],
'refund_apply':[('refund_admission','BR-REV-005'),('cumulative_delta','BR-REV-006 BR-REW-006'),('capture_id','BR-REV-007 BR-REV-008'),('i < count','BR-REV-007'),('principal_due','BR-REV-007'),('fee_due','BR-REV-007'),('cash_refund_total','BR-REV-008'),('refund_post','BR-REV-008'),('array_append','FR-IO-011')],
'authorize_apply':[('!a','BR-AUT-001'),('!card','BR-AUT-001'),('!merchant','BR-AUT-001'),('card->account_id','BR-AUT-001'),('r.reason','BR-AUT-001 BR-AUT-004'),('DECLINED','BR-AUT-004'),('REVIEW','BR-AUT-005'),('array_append','BR-AUT-008 FR-IO-011'),('hold_ttl','BR-AUT-006'),('ledger_pair','BR-AUT-002')],
}
# Decision annotations identify local behavior, rather than copying every function
# dependency onto every branch of a heterogeneous dispatcher or transition.
REGIONS.update({
 'record_decision': [('DECLINED','BR-LIM-006'),('APPROVED','BR-LIM-006 BR-LIM-008'),('REVIEW','BR-AUT-005 BR-LIM-005')],
 'command_same_key': [('a->op','BR-IDM-004'),('request_id','BR-IDM-001 BR-IDM-002')],
 'main': [('signal','FR-IO-009'),('argc','FR-IO-009'),('argv','FR-IO-009'),('seed','FR-IO-009 FR-IO-010'),('loaded','FR-IO-010'),('commands','FR-IO-009'),('status == 0','FR-IO-007'),('status == -2','FR-IO-009'),('status < 0','FR-IO-001 FR-IO-006'),('ferror','FR-IO-009'),('fflush','FR-IO-009')],
 'seed_load': [('status','FR-IO-010'),('phase','FR-IO-010'),('config_valid','FR-IO-010'),('ok','FR-IO-010')],
 'tokenize': [('LINE_MAX_BYTES','FR-IO-006'),('tokens[i].key','FR-IO-002'),('equal','FR-IO-001'),('cursor','FR-IO-007'),('count','FR-IO-001'),('c <','FR-IO-001'),('c >','FR-IO-001')],
 'parse_command': [('allowed','FR-IO-003'),('field','FR-IO-003'),('required','FR-IO-001'),('INVALID_OP','FR-IO-001')],
 'read_line': [('bytes','FR-IO-006'),('size','FR-IO-006'),('ch','FR-IO-001 FR-IO-006'),('ferror','FR-IO-009'),('invalid','FR-IO-006')],
 'project_account': [('account_id','BR-BAT-004'),('invoice_id','BR-BIL-008 BR-LIM-001')],
 'reconcile': [('account_id','BR-BAT-004 BR-BAT-005'),('difference','BR-BAT-005'),('balance','BR-BAT-005 BR-BAT-006'),('cached','BR-BAT-005')],
 'tick_apply': [('c->now <','BR-BAT-008'),('expires_at','BR-REV-004 BR-BAT-008'),('count','BR-REV-004 BR-BAT-008'),('expiring','FR-IO-011 BR-BAT-008'),('ledger_pair','BR-BAT-008'),('INT64_MAX','BR-MNY-008')],
 'cancel_apply': [('state','BR-REV-001 BR-REV-003'),('ledger_pair','BR-REV-001'),('money_valid','BR-MNY-001')],
 'close_apply': [('account_id','BR-BIL-001 BR-BIL-002 BR-BAT-004'),('cycle','BR-BIL-001 BR-BIL-002 BR-BIL-003'),('money_add','BR-MNY-002 BR-BIL-003'),('array_append','FR-IO-011')],
 'pay_apply': [('r.reason','BR-BIL-009'),('allocate_','BR-BIL-007'),('remaining','BR-BIL-007'),('array_append','FR-IO-011')],
 'assess_apply': [('late_fee_assessed','BR-BIL-011 BR-BIL-012'),('due_day','BR-BIL-011'),('invoice_outstanding','BR-BIL-011'),('ledger_pair','BR-BIL-011 FR-IO-011')],
 'allocate_lots': [('account_id','BR-BAT-004 BR-BIL-008'),('invoice_id','BR-BIL-008'),('component','BR-BIL-007'),('remaining','BR-BIL-007'),('paid','BR-BIL-007'),('ledger_pair','BR-BIL-007')],
 'allocate_late': [('account_id','BR-BAT-004'),('remaining','BR-BIL-007'),('ledger_pair','BR-BIL-007')],
 'config_valid': [('fx_','BR-MNY-007'),('bps','BR-MNY-007'),('capacities','FR-IO-011')],
 'capture_installment_allowed': [('n >=','BR-INS-001'),('n <=','BR-INS-001'),('minimum_installment','BR-INS-003 BR-INS-008')],
 'installment_allowed': [('country','BR-INS-002')],
 'reward_raw': [('RESTRICTED','BR-REW-003'),('PREMIUM','BR-REW-001 BR-REW-002 BR-REW-008')],
})
REGIONS.update({
 'capture_admission': [('amount == 0','FR-IO-001'),('money_valid','FR-IO-001'),('state','BR-CAP-001'),('expires_at','BR-CAP-001'),('remaining','BR-CAP-002'),('money_sub','BR-CAP-002')],
 'refund_admission': [('money_valid','FR-IO-001'),('amount == 0','FR-IO-001'),('remaining','BR-REV-005'),('money_sub','BR-REV-005')],
 'daily_totals': [('account_id','BR-BAT-004'),('day','BR-LIM-004 BR-LIM-006'),('APPROVED','BR-LIM-006 BR-LIM-008'),('REVIEW','BR-LIM-005 BR-LIM-006')],
 'cacheable': [('decision','BR-IDM-005 BR-IDM-006'),('op','BR-IDM-008')],
})
# Directly homogeneous algorithms may associate all their local decisions with
# their one calculation. Dispatchers and financial transitions must be narrowed.
HOMOGENEOUS = {
 'money_valid': ['BR-MNY-001'], 'checked_mul':['BR-MNY-008'],
 'money_add':['BR-MNY-002'], 'money_sub':['BR-MNY-003'],
 'floor_rate':['BR-MNY-004 BR-MNY-007'], 'ceil_rate':['BR-MNY-005 BR-MNY-007'],
 'money_fx':['BR-MNY-006 BR-MNY-007'], 'split_part':['BR-INS-004 BR-INS-005 BR-INS-007'],
 'available_credit':['BR-LIM-001'], 'credit_admission':['BR-LIM-002'],
 'operation_admission':['BR-LIM-003'], 'daily_admission':['BR-LIM-004'],
 'count_admission':['BR-LIM-005'], 'recent_count':['BR-RSK-005'],
 'risk_classify':['BR-RSK-006'], 'capture_state':['BR-CAP-004'],
 'refund_lot_order':['BR-REV-007'], 'invoice_order':['BR-BIL-007'], 'lot_order':['BR-BIL-007'],
 'invoice_minimum':['BR-BIL-006'], 'invoice_due_day':['BR-BIL-005 BR-INS-006'],
 'reward_grant':['BR-REW-004'], 'reward_gross':['BR-REW-005 BR-REW-007'],
 'write_auth_ids':['BR-BAT-007'], 'ledger_balanced':['BR-BAT-006'],
 'identifier_valid':['FR-IO-004'], 'bounded_id':['FR-IO-004'], 'decimal_parse':['FR-IO-005'],
 'json_string':['FR-IO-008'], 'array_append':['FR-IO-011'],
}
HOMOGENEOUS.update({
 'close_admission':['BR-BIL-001'], 'payment_admission':['BR-BIL-009'],
 'authorization_hold':['BR-AUT-002 BR-CAP-005 BR-REV-001 BR-REV-002'],
 'refund_post':['BR-REV-008'], 'reconcile':['BR-BAT-005'],
 'command_valid':['FR-IO-001'], 'command_equal':['BR-IDM-002 BR-IDM-003'],
 'required_fields':['FR-IO-001'], 'allowed_fields':['FR-IO-003'], 'command_field':['FR-IO-001'],
 'write_result':['FR-IO-008'], 'bool_field':['FR-IO-008'],
 'config_field':['FR-IO-010'], 'seed_config':['FR-IO-010'], 'seed_account':['FR-IO-010'],
 'seed_card':['FR-IO-010'], 'seed_merchant':['FR-IO-010'], 'seed_load':['FR-IO-010'],
 'engine_clone':['FR-IO-011'],
})
# These are deliberately conservative witnesses of causal composition. Counts
# below use only these reviewed witnesses, not all names in SUPPORT.
INTERACTIONS = {
 'BR-PRC-002': ('quote money_fx','The currency branch selects the rate; money_fx performs the bounded conversion and rounding.'),
 'BR-PRC-004': ('price_components floor_rate','Currency/tier admission and integer percentage computation reside in different functions.'),
 'BR-LIM-001': ('project_account authorization_hold lot_principal lot_fee available_credit','Credit availability requires state aggregation and the zero floor calculation.'),
 'BR-LIM-002': ('authorize_apply credit_admission money_add','Authorization sends principal and fee to the checked total comparison before reserving.'),
 'BR-LIM-003': ('authorize_apply quote operation_admission','The per-operation gate consumes converted principal, not nominal input.'),
 'BR-LIM-004': ('authorize_apply project_account daily_totals daily_admission','The comparison consumes historical gross principal for this account/day.'),
 'BR-LIM-005': ('authorize_apply project_account daily_totals count_admission','The daily count gate consumes the aggregation of prior decisions.'),
 'BR-RSK-005': ('authorize_apply recent_count risk_score','Window filtering supplies the velocity component before the current decision is recorded.'),
 'BR-AUT-001': ('execute authorize_apply eligibility quote credit_admission risk_classify','Envelope/idempotency precede the ordered business gates and final risk decision.'),
 'BR-AUT-002': ('authorize_apply ledger_pair project_account authorization_hold','The created authorization determines held balance and paired reservation entries.'),
 'BR-AUT-005': ('authorize_apply record_decision daily_totals recent_count','Review writes history consumed by both counters but returns before authorization creation.'),
 'BR-AUT-008': ('execute engine_clone authorize_apply array_append','A capacity failure in a prepared transition discards the clone including prior staged changes.'),
 'BR-IDM-001': ('execute command_same_key command_equal','Typed key lookup and canonical semantic payload comparison select the stored result before mutation.'),
 'BR-IDM-003': ('parse_command decimal_parse command_default command_equal','Parsing normalizes numbers and defaults before semantic equality.'),
 'BR-CAP-003': ('capture_apply cumulative_delta proportional','The capture fee is the difference of two cumulative allocations.'),
 'BR-CAP-004': ('capture_apply capture_state authorization_hold','Captured principal determines the authorization state and remaining hold projection.'),
 'BR-CAP-005': ('capture_apply project_account authorization_hold lot_principal lot_fee','One transition replaces part of the held authorization with receivable lots.'),
 'BR-CAP-006': ('capture_apply ledger_pair ledger_post','The capture posts principal, fee and reserve release as balanced entry pairs.'),
 'BR-CAP-007': ('execute engine_clone capture_apply array_append','Failures during staged lot/entry growth preserve the original state.'),
 'BR-REV-001': ('cancel_apply authorization_hold ledger_pair','Remaining reserve is derived before the paired release and terminal state change.'),
 'BR-REV-004': ('tick_apply authorization_hold ledger_pair','Expiry selection precedes reserve derivation and release entries for each selected authorization.'),
 'BR-REV-006': ('refund_apply cumulative_delta proportional','Capture-specific fee refunds use cumulative differences and exact integer proportional allocation.'),
 'BR-REV-007': ('refund_apply refund_lot_order lot_principal lot_fee','Sorted capture lots and unpaid component projections control reverse allocation.'),
 'BR-REV-008': ('refund_apply refund_post ledger_pair project_account','Unpaid cancellation and paid cash portions feed different ledger postings and the account projection.'),
 'BR-INS-005': ('capture_apply split_part','Separate calls divide principal and fee, preserving independent remainders.'),
 'BR-INS-006': ('capture_apply invoice_due_day','Capture-time lot cycles determine invoice due dates through the shared calendar computation.'),
 'BR-BIL-004': ('close_apply invoice_minimum','The issued snapshot feeds the minimum-payment computation without future lots.'),
 'BR-BIL-006': ('invoice_minimum ceil_rate','Ceiling percentage calculation composes with the floor and total cap.'),
 'BR-BIL-007': ('pay_apply allocate_late allocate_lots invoice_order lot_order','Class priority and sorted within-class allocation require distinct procedures.'),
 'BR-BIL-008': ('pay_apply allocate_lots project_account','Only invoiced lots are allocated while account debt includes future lots.'),
 'BR-BIL-011': ('assess_apply invoice_outstanding ledger_pair','Overdue unpaid balance guards the single fine and its paired entries.'),
 'BR-REW-004': ('capture_apply reward_raw reward_gross reward_grant','Raw points and gross cycle history jointly determine the granted amount.'),
 'BR-REW-006': ('refund_apply cumulative_delta proportional','Refund points use the same exact cumulative allocation algorithm on actual granted points.'),
 'BR-BAT-005': ('reconcile project_account authorization_hold lot_principal lot_fee','Reconciliation compares recomputed state components and cached projections.'),
 'BR-BAT-006': ('ledger_pair ledger_post ledger_balanced','Posting creates paired rows while reconciliation checks each event independently.'),
 'BR-BAT-008': ('execute engine_clone tick_apply','Time advancement and the full expiry batch commit together through the prepared engine.'),
}
DECISIONS={'IF_STMT','FOR_STMT','WHILE_STMT','DO_STMT','SWITCH_STMT','CASE_STMT','DEFAULT_STMT','CONDITIONAL_OPERATOR'}
LOOPS={'FOR_STMT','WHILE_STMT','DO_STMT'}


def dump(name,obj):
 (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def compact(text):
 return re.sub(r'\s+','',text)


def own_operator(node):
 """Look between immediate operands, never through the tokens of descendants."""
 children=list(node.get_children())
 if len(children)!=2: return None
 left,right=children
 for token in node.get_tokens():
  if token.extent.start.offset >= left.extent.end.offset and token.extent.end.offset <= right.extent.start.offset:
   if token.spelling in {'&&','||','=','+=','-=','*=','/=','%='}: return token.spelling
 return None


def guard_node(node):
 children=list(node.get_children())
 if node.kind.name in {'IF_STMT','WHILE_STMT','SWITCH_STMT','CONDITIONAL_OPERATOR','CASE_STMT'}:
  return children[0] if children else node
 if node.kind.name=='DO_STMT': return children[-1] if children else node
 if node.kind.name=='FOR_STMT':
  # Only an expression located between the first two header semicolons is a guard.
  semicolons=[t.extent.start.offset for t in node.get_tokens() if t.spelling==';']
  if len(semicolons)>=2:
   candidates=[c for c in children if c.extent.start.offset>semicolons[0] and c.extent.end.offset<=semicolons[1]]
   if candidates: return candidates[0]
  return None
 if node.kind.name=='DEFAULT_STMT': return None
 return node


def classify_rules(symbol,predicate):
 rules=[]
 for token,ids in REGIONS.get(symbol,[]):
  if compact(token) in compact(predicate): rules.extend(ids.split())
 if not rules:
  for ids in HOMOGENEOUS.get(symbol,[]): rules.extend(ids.split())
 return sorted(set(rules))


def main():
 OUT.mkdir(exist_ok=True)
 inc=subprocess.check_output(['cc','-print-file-name=include'],text=True).strip()
 functions=[]; decisions=[]; files=[]; calls=[]; errors=[]; observables={}
 for path in sorted((ROOT/'subject/src').glob('*.c')):
  rel=str(path.relative_to(ROOT)); raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
  files.append({'path':rel,'sha256':digest,'bytes':len(raw)})
  unit=cindex.Index.create().parse(str(path),args=['-std=c17','-I'+str(ROOT/'subject/include'),'-I'+inc])
  errors += [str(d) for d in unit.diagnostics if d.severity>=cindex.Diagnostic.Error]
  def source(n): return raw[n.extent.start.offset:n.extent.end.offset].decode()
  def anchor(n):
   lo,hi=n.extent.start,n.extent.end
   if not (0<=lo.offset<hi.offset<=len(raw)): errors.append(f'Invalid span {rel}:{lo.line}')
   return {'file':rel,'start_line':lo.line,'end_line':hi.line,'start_byte':lo.offset,'end_byte':hi.offset,'file_sha256':digest,'text_sha256':hashlib.sha256(raw[lo.offset:hi.offset]).hexdigest()}
  for f in unit.cursor.get_children():
   if f.kind.name!='FUNCTION_DECL' or not f.is_definition() or not f.location.file or Path(f.location.file.name)!=path: continue
   functions.append({'symbol':f.spelling,'anchor':anchor(f),'exported':f.storage_class!=cindex.StorageClass.STATIC,'contracts':CONTRACTS[path.name]})
   observables[f.spelling]=[]
   for n in f.walk_preorder():
    kind=n.kind.name
    if kind=='CALL_EXPR' and n.spelling: calls.append({'caller':f.spelling,'callee':n.spelling,'line':n.location.line,'file':rel})
    operator=own_operator(n) if kind in {'BINARY_OPERATOR','COMPOUND_ASSIGNMENT_OPERATOR'} else None
    if kind=='RETURN_STMT':
     children=list(n.get_children())
     expr=source(children[0]) if children else ''
     safe=bool(re.fullmatch(r'[a-z_][a-z0-9_]*(?:[.][a-z_][a-z0-9_]*)*',expr)) and expr not in {'true','false'}
     observables[f.spelling].append({'kind':'RETURN_VALUE','anchor':anchor(n),'expression':expr if safe else '$return','expression_source':expr,'source':source(n),'moment':'BEFORE','observed_output':'returned value'})
    elif operator in {'=','+=','-=','*=','/=','%='}:
     lhs=list(n.get_children())[0]
     expr=source(lhs)
     if expr.startswith('*'):
      observables[f.spelling].append({'kind':'POINTER_WRITE','anchor':anchor(n),'expression':expr,'expression_source':expr,'source':source(n),'moment':'AFTER','observed_output':expr})
    if kind=='CALL_EXPR' and n.spelling in {'fputs','fputc'}:
     args=list(n.get_arguments())
     if len(args)==2:
      observables[f.spelling].append({'kind':'STREAM_WRITE','anchor':anchor(n),'expression':source(args[1]),'expression_source':source(args[1]),'source':source(n),'moment':'AFTER','observed_output':'output stream'})
    is_logic=kind=='BINARY_OPERATOR' and operator in {'&&','||'}
    if kind not in DECISIONS and not is_logic: continue
    condition=guard_node(n)
    predicate=source(condition) if condition else ''
    rules=classify_rules(f.spelling,predicate)
    decisions.append({'symbol':f.spelling,'kind':'LOGICAL_OPERATOR' if is_logic else kind,'operator':operator if is_logic else None,'anchor':anchor(n),'predicate_anchor':anchor(condition) if condition else None,'predicate':predicate,'rules':rules,'contracts':CONTRACTS[path.name]})
 by_name={f['symbol']:f for f in functions}
 if len(by_name)!=len(functions): errors.append('Ambiguous function symbols; qualify map by source file')
 known_rules={r['id'] for r in RULES}
 probe_map=json.loads((ROOT/'harness/probe-map.json').read_text())
 scenario_index=[]; scenario_ids=set(); test_refs={rid:[] for rid in known_rules}
 for feature in sorted((ROOT/'docs/oracle/features').glob('*.feature')):
  document=Parser().parse(feature.read_text()); document['uri']=str(feature.relative_to(ROOT))
  for case in Compiler().compile(document):
   tags=[t['name'][1:] for t in case['tags']]
   ids=[t for t in tags if t.startswith('SC-')]
   covered=[t for t in tags if t in known_rules]
   covered += [t[len('covers_'):] for t in tags if t.startswith('covers_')]
   for rid in covered:
    if rid not in known_rules: errors.append(f'Unknown rule tag {rid}')
   action=case['steps'][1]['text']
   operation=action[len('avalio "'):-1] if action.startswith('avalio "') and action.endswith('"') else None
   if operation not in probe_map: errors.append(f'Undefined binding {operation}')
   binding=probe_map.get(operation,{})
   for name in binding.get('symbols',[]):
    if name not in by_name: errors.append(f'{operation}: missing production binding {name}')
   record={'ids':ids,'file':case['uri'],'line':case['location']['line'],'rules':sorted(set(covered)),'operation':operation,'binding':{'file':'harness/probes.py','symbol':'probe','map':'harness/probe-map.json','kind':binding.get('kind'),'production_symbols':binding.get('symbols',[])},'runner':'harness/run.py'}
   scenario_index.append(record); scenario_ids.update(ids)
   for rid in covered:
    if rid in test_refs: test_refs[rid].append(record)
 trace=[]; index=[]; criteria=[]; public=[]; supports=[]
 for rule in RULES:
  rid=rule['id']; _,family,number=rid.split('-')
  symbols=SUPPORT[family][int(number)-1].split()
  for symbol in symbols:
   if symbol not in by_name: errors.append(f'{rid}: missing symbol {symbol}')
  symbols=[s for s in symbols if s in by_name]
  symbols += sorted({d['symbol'] for d in decisions if rid in d['rules']} - set(symbols))
  tests=[c['id'] for c in rule['cases']]
  for test in tests:
   if test not in scenario_ids: errors.append(f'{rid}: missing compiled Gherkin scenario {test}')
  tests=sorted(set(tests+[test for record in test_refs[rid] for test in record['ids']]))
  cls='TECHNICAL' if rid.startswith('FR-') else 'DOMAIN'
  scope='UNIT defensive historical policy; not reachable through normal restricted merchant authorization' if rid=='BR-REW-003' else 'Contract universal within valid input/state; supplied cases are examples'
  anchors=[dict(by_name[s]['anchor'],symbol=s,granularity='function support window') for s in symbols]
  regions=[{'symbol':d['symbol'],'kind':d['kind'],'anchor':d['predicate_anchor'] or d['anchor']} for d in decisions if rid in d['rules']]
  index.append({'id':rid,'class':cls,'capability':family,'statement':rule['norm'],'inputs':sorted({k for c in rule['cases'] for k in c['given']}),'guards':regions,'effect_fields':sorted({k for c in rule['cases'] for k in c['expected']}),'operation':rule['operation'],'scenarios':tests,'scope':scope})
  trace.append({'rule':rid,'class':cls,'symbols':symbols,'regions':regions or anchors,'essential_functions':anchors,'scenarios':tests,'test_refs':test_refs[rid],'binding_operation':rule['operation'],'support_review':'Reviewed against actual calculation, transition and caller relationships. Function windows are locations of support, not claims that every statement is essential.'})
  supports.append({'rule':rid,'essential':anchors,'focused_regions':regions,'alternatives':[],'irrelevant':{'paths':['docs/oracle/','harness/','evaluation/'],'production_boundary':'Formatting is outside financial calculations; retain parsing/caller guards when the selected criterion depends on them.'},'review':{'status':'REVIEWED_FUNCTION_SUPPORT','granularity':'Required causal contributors; function windows contain both relevant and irrelevant statements. Focused predicates narrow shared functions but do not replace the data-flow support.','alternatives_status':'No exhaustive enumeration of equivalent support sets; adjudicate other valid supports rather than rejecting by node identity.','absence_claims':'Purity, noninterference and no-repeat claims additionally require inspection of the transition writes and independent state-comparison tests.','slicing_status':'Not a computed or certified complete slice.'}})
  for symbol in symbols: by_name[symbol].setdefault('rules',[]).append(rid)
  if not symbols: continue
  symbol=symbols[0]
  candidates=observables[symbol]
  # Eligibility and similar direct-return guards can expose a precise selected
  # return site without putting the returned enum/value into public metadata.
  focused=[o for o in candidates if any(d['symbol']==symbol and rid in d['rules'] and d['anchor']['start_byte']<=o['anchor']['start_byte'] and d['anchor']['end_byte']>=o['anchor']['end_byte'] for d in decisions)]
  pointer=[o for o in candidates if o['kind']=='POINTER_WRITE']
  returns=[o for o in candidates if o['kind']=='RETURN_VALUE']
  money_outputs={'checked_mul','money_add','money_sub','floor_rate','ceil_rate','money_fx','proportional','cumulative_delta','decimal_parse'}
  replay=[o for o in returns if 'key->result' in o['expression_source']]
  selected=(replay if rid in {'BR-IDM-001','BR-IDM-004','BR-IDM-007','BR-BAT-003'} and replay else focused[-1:] if symbol=='eligibility' and focused else pointer[-1:] if symbol in money_outputs and pointer else returns[-1:] if returns else candidates[-1:])
  if not selected:
   errors.append(f'{rid}: no actual return/write observation in {symbol}'); continue
  observation=selected[0]; a=observation['anchor']; ident=f'criterion-{len(criteria)+1:03d}'
  criterion={'id':ident,'file':a['file'],'function':symbol,'location':a['start_line'],'expression':observation['expression'],'selector':observation['kind'],'moment':observation['moment'],'observed_output':observation['observed_output'],'anchor':a}
  public.append(criterion)
  trace[-1]['criterion_ids']=[ident]
  criteria.append(dict(criterion,rule=rid,expression_source=observation['expression_source'],source=observation['source']))
 for f in functions:
  f['rules']=sorted(set(f.get('rules',[])))
  f['classification']='DOMAIN' if any(r.startswith('BR-') for r in f['rules']) else 'TECHNICAL' if f['rules'] else 'SUPPORT'
  f['justification']='Contains causal support for the listed rules; individual decisions are classified independently below.' if f['rules'] else 'Technical support for the linked contract; no new financial policy is assigned to this helper.'
 for d in decisions:
  f=by_name[d['symbol']]
  d['serves_rules']=f['rules']
  d['classification']='DOMAIN' if any(r.startswith('BR-') for r in d['rules']) else 'TECHNICAL' if d['rules'] else 'SUPPORT'
  d['justification']='Local predicate matched a reviewed behavior or belongs to one homogeneous calculation.' if d['rules'] else 'Shared iteration, validation, dispatch or failure handling under the linked contract. Its caller/function serves the separate rule list; this predicate is not asserted to implement all of those rules.'
 inventory={'generator':'libclang AST','decision_definition':'Control/loop/case nodes, conditional expressions and own &&/|| operators. A binary expression does not count merely because a descendant is logical.','files':files,'functions':functions,'decisions':decisions,'calls':calls,'exports':[f['symbol'] for f in functions if f['exported']]}
 broken=[rid for item in functions+decisions for rid in item['rules'] if rid not in known_rules]
 errors+=['Unknown rule '+rid for rid in broken]
 interactions=[]
 for rid,(names,reason) in INTERACTIONS.items():
  syms=names.split()
  if rid not in known_rules or any(s not in by_name for s in syms):
   errors.append(f'Invalid interaction witness {rid}'); continue
  relevant=[dict(by_name[s]['anchor'],symbol=s) for s in syms]
  interactions.append({'rule':rid,'symbols':syms,'anchors':relevant,'reason':reason,'cross_file':len({a['file'] for a in relevant})>1,'call_edges':[c for c in calls if c['caller'] in syms and c['callee'] in syms]})
 loop_rules=sorted({rid for d in decisions if d['kind'] in LOOPS for rid in d['rules']})
 # Explicit loop-bearing support: temporal histories, account projection,
 # allocation, journal reconciliation and the expiry batch are genuine aggregates.
 for rid,names in {'BR-LIM-001':'project_account','BR-LIM-004':'daily_totals','BR-LIM-005':'daily_totals','BR-LIM-006':'daily_totals','BR-LIM-007':'daily_totals','BR-RSK-005':'recent_count','BR-ELG-009':'eligibility','BR-CAP-005':'project_account','BR-REV-007':'refund_apply','BR-BIL-003':'close_apply','BR-BIL-007':'allocate_late allocate_lots','BR-REW-005':'reward_gross','BR-BAT-005':'reconcile project_account','BR-BAT-006':'ledger_balanced','BR-BAT-008':'tick_apply'}.items():
  if any(d['kind'] in LOOPS and d['symbol'] in names.split() for d in decisions): loop_rules.append(rid)
 loop_rules=sorted(set(loop_rules))
 stats={'rules':len(trace),'functions':len(functions),'decisions':len(decisions),'logical_decisions':sum(d['kind']=='LOGICAL_OPERATOR' for d in decisions),'public_criteria':len(public),'compiled_scenarios':len(scenario_index),'multifunction_rules':len(interactions),'cross_file_rules':sum(i['cross_file'] for i in interactions),'loop_rules':len(loop_rules),'reviewed_loop_rules':loop_rules,'support_multifunction_rules':sum(len(t['symbols'])>1 for t in trace),'support_cross_file_rules':sum(len({a['file'] for a in t['essential_functions']})>1 for t in trace),'unmapped_rules':sum(not t['symbols'] for t in trace),'orphan_functions':sum(not f['rules'] and not f['contracts'] for f in functions),'orphan_decisions':sum(not d['rules'] and not d['contracts'] for d in decisions),'errors':errors,'limitations':['Support windows are manually reviewed causal locations, not complete backward slices.','Criteria select observable return/write AST nodes. $return is a selector for the returned value, not a fabricated source variable. Exact expression sources remain evaluator-private when they contain formulas or constant outcomes.']}
 for name,obj in [('rule-index.json',index),('traceability.json',trace),('inventory.json',inventory),('criteria.json',criteria),('criteria-public.json',public),('expected-supports.json',supports),('interaction-evidence.json',interactions),('scenario-index.json',scenario_index),('coverage.json',stats)]: dump(name,obj)
 print(json.dumps(stats,ensure_ascii=False))
 if errors: raise SystemExit(1)
if __name__=='__main__': main()
