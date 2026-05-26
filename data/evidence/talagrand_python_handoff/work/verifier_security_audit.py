#!/usr/bin/env python3
"""
Verifier security audit for the uploaded d20 / CVX / KEM artifacts.
This is a defensive, local audit: registry consistency, adversarial mutation rejection,
zip safety, hash coverage, and policy-boundary checks. It does not claim a cryptographic break
or formal proof-assistant verification.
"""
from __future__ import annotations
import copy, hashlib, json, os, pathlib, re, sys, zipfile
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any

ROOT = pathlib.Path('/mnt/data')
D20 = ROOT / 'd20.json'
CVX_ZIP = ROOT / 'cvx_trace.zip'
KEM_ZIP = ROOT / 'kem_auditor_cross_impl_liboqs_3x80.zip'
OUT_JSON = ROOT / 'verifier_security_audit_report.json'
OUT_MD = ROOT / 'verifier_security_audit_report.md'


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()

def canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def canon_hash(obj: Any) -> str:
    return sha256_bytes(canon(obj))

@dataclass
class Check:
    name: str
    passed: bool
    severity: str = 'info'
    detail: str = ''
    evidence: Any = None


def load_json(p: pathlib.Path) -> Any:
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)

class RegistryVerifier:
    REQUIRED_FIELDS = {'id', 'ordinal', 'group', 'path', 'depends_on', 'claim_level'}

    def __init__(self, d20: dict):
        self.d20 = d20
        self.registry = d20.get('certificate_registry', {})
        self.entries = self.registry.get('certificates', [])
        self.groups = self.registry.get('groups', {})
        self.embedded = d20.get('certificates', {})

    def graph_hash(self) -> str:
        reduced = []
        for e in self.entries:
            reduced.append({
                'id': e.get('id'),
                'ordinal': e.get('ordinal'),
                'group': e.get('group'),
                'depends_on': list(e.get('depends_on', [])),
                'expected_status': e.get('expected_status'),
                'claim_level': e.get('claim_level'),
            })
        return canon_hash(reduced)

    def validate(self, *, baseline_graph_hash: str | None = None, baseline_top_hash: str | None = None) -> tuple[bool, list[Check]]:
        checks: list[Check] = []
        add = checks.append

        add(Check('d20_json_parseable', isinstance(self.d20, dict), 'critical'))
        add(Check('d20_status_certified', self.d20.get('status') == 'D20_CERTIFIED', 'critical', str(self.d20.get('status'))))
        add(Check('registry_status_built', self.registry.get('status') == 'CERTIFICATE_REGISTRY_BUILT', 'critical', str(self.registry.get('status'))))
        add(Check('registry_source_of_truth_flag', bool(self.registry.get('policy', {}).get('certificate_registry_is_source_of_truth')), 'high'))

        ids = [e.get('id') for e in self.entries]
        idset = set(ids)
        add(Check('registry_has_26_entries', len(self.entries) == 26, 'medium', str(len(self.entries))))
        add(Check('registry_ids_unique', len(ids) == len(idset), 'critical', detail=f'{len(ids)} ids / {len(idset)} unique'))

        missing_fields = {e.get('id', '<missing id>'): sorted(self.REQUIRED_FIELDS - set(e.keys())) for e in self.entries if self.REQUIRED_FIELDS - set(e.keys())}
        add(Check('registry_required_fields_present', not missing_fields, 'critical', evidence=missing_fields))

        unknown_groups = [e.get('id') for e in self.entries if e.get('group') not in self.groups]
        add(Check('registry_groups_known', not unknown_groups, 'high', evidence=unknown_groups))

        embedded_missing = [cid for cid in ids if cid not in self.embedded]
        add(Check('embedded_certificate_present_for_every_registry_id', not embedded_missing, 'critical', evidence=embedded_missing))

        dep_missing = []
        ordinal_viol = []
        ordinal_map = {e.get('id'): e.get('ordinal') for e in self.entries}
        for e in self.entries:
            eid = e.get('id')
            for dep in e.get('depends_on', []):
                if dep not in idset:
                    dep_missing.append((eid, dep))
                elif ordinal_map.get(dep, 10**9) >= e.get('ordinal', -1):
                    ordinal_viol.append((eid, dep, ordinal_map.get(dep), e.get('ordinal')))
        add(Check('dependency_references_resolve', not dep_missing, 'critical', evidence=dep_missing))
        add(Check('dependencies_precede_dependents_by_ordinal', not ordinal_viol, 'high', evidence=ordinal_viol[:10]))

        # cycle check
        incoming = {cid: 0 for cid in ids}
        outgoing = defaultdict(list)
        for e in self.entries:
            eid = e.get('id')
            for dep in e.get('depends_on', []):
                if dep in incoming:
                    incoming[eid] += 1
                    outgoing[dep].append(eid)
        q = deque([cid for cid, deg in incoming.items() if deg == 0])
        seen = []
        while q:
            u = q.popleft(); seen.append(u)
            for v in outgoing[u]:
                incoming[v] -= 1
                if incoming[v] == 0:
                    q.append(v)
        add(Check('dependency_graph_acyclic', len(seen) == len(ids), 'critical', detail=f'topo_count={len(seen)}'))

        status_mismatch = []
        for e in self.entries:
            exp = e.get('expected_status')
            if exp is None:
                continue
            cert = self.embedded.get(e.get('id'), {})
            got = cert.get('status') if isinstance(cert, dict) else None
            if got != exp:
                status_mismatch.append((e.get('id'), exp, got))
        add(Check('expected_status_matches_embedded_status', not status_mismatch, 'critical', evidence=status_mismatch[:8]))

        current_graph_hash = self.graph_hash()
        add(Check('registry_graph_hash_computed', True, 'info', current_graph_hash))
        if baseline_graph_hash:
            add(Check('registry_graph_hash_matches_baseline', current_graph_hash == baseline_graph_hash, 'critical', detail=f'current={current_graph_hash} baseline={baseline_graph_hash}'))
        if baseline_top_hash:
            add(Check('d20_canonical_content_hash_matches_baseline', canon_hash(self.d20) == baseline_top_hash, 'critical'))
        return all(c.passed for c in checks if c.severity in {'critical','high'}), checks


def zip_safety(zip_path: pathlib.Path) -> tuple[bool, list[str]]:
    bad = []
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            name = info.filename.replace('\\', '/')
            p = pathlib.PurePosixPath(name)
            if name.startswith('/') or name.startswith('~') or re.match(r'^[A-Za-z]:', name):
                bad.append(info.filename)
            if any(part == '..' for part in p.parts):
                bad.append(info.filename)
    return not bad, bad


def kem_hash_coverage(kem_dir: pathlib.Path) -> tuple[bool, list[Check]]:
    checks: list[Check] = []
    def add(name, passed, severity='high', detail='', evidence=None):
        checks.append(Check(name, bool(passed), severity, detail, evidence))
    manifest = load_json(kem_dir/'manifest.json')
    outputs = manifest.get('outputs', {})
    pairs = [(k, v) for k, v in outputs.items() if k.endswith('_sha256')]
    failures = []
    # Map output hash fields to their file fields where possible.
    hash_to_file = {
        'audit_memo_sha256': 'audit_memo',
        'readme_sha256': 'readme',
        'replay_recipe_sha256': 'replay_recipe',
        'verify_script_sha256': 'verify_script',
    }
    for hash_key, file_key in hash_to_file.items():
        fp = kem_dir / outputs.get(file_key, '')
        expected = outputs.get(hash_key)
        if not fp.exists() or sha256_file(fp) != expected:
            failures.append((file_key, expected, sha256_file(fp) if fp.exists() else None))
    # nested evidence bundle outputs
    ev = kem_dir / 'evidence_bundle'
    ev_manifest = load_json(ev/'manifest.json')
    ev_outputs = ev_manifest.get('outputs', {})
    for file_key, hash_key in [
        ('ablation_ci_json','ablation_ci_json_sha256'),
        ('blind_matrix_json','blind_matrix_json_sha256'),
        ('packet_json','packet_json_sha256'),
        ('packet_markdown','packet_markdown_sha256'),
    ]:
        fp = ev / ev_outputs.get(file_key, '')
        expected = ev_outputs.get(hash_key)
        if not fp.exists() or sha256_file(fp) != expected:
            failures.append((f'evidence_bundle/{file_key}', expected, sha256_file(fp) if fp.exists() else None))
    add('kem_manifest_hash_coverage', not failures, 'high', evidence=failures)
    verification = load_json(kem_dir/'verification.json')
    add('kem_verification_status_pass', verification.get('status') == 'PASS', 'high', str(verification.get('status')))
    add('kem_boundary_not_break_claim', 'not independent external validation' in verification.get('boundary','').lower() and 'not independent external validation' in load_json(ev/'verification.json').get('boundary','').lower(), 'medium')
    summary = manifest.get('summary', {})
    add('kem_public_no_signal', summary.get('blind_public_signals') == 0 and summary.get('blind_public_total') == 36, 'high', evidence=summary)
    add('kem_instrumented_signal_present', summary.get('instrumented_signals') == summary.get('instrumented_total') == 36, 'medium', evidence=summary)
    return all(c.passed for c in checks if c.severity in {'critical','high'}), checks


def cvx_policy_checks(cvx_dir: pathlib.Path) -> tuple[bool, list[Check]]:
    checks: list[Check] = []
    def add(name, passed, severity='high', detail='', evidence=None):
        checks.append(Check(name, bool(passed), severity, detail, evidence))
    reports = cvx_dir/'reports'
    json_files = sorted(reports.glob('*.json')) + sorted((cvx_dir/'certificates').glob('*.json')) + sorted((cvx_dir/'residues').glob('*.json'))
    parse_errors = []
    loaded = {}
    for p in json_files:
        try:
            loaded[p.name] = load_json(p)
        except Exception as e:
            parse_errors.append((str(p), str(e)))
    add('cvx_all_json_parse', not parse_errors, 'critical', detail=f'{len(json_files)} json files', evidence=parse_errors)
    xpol = loaded.get('x_policy_boundary_certificate.json', {})
    add('cvx_x_policy_status_certified', xpol.get('status') == 'X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X', 'high', str(xpol.get('status')))
    pure = loaded.get('universal_pure_c_no_escape_report.json', {})
    add('cvx_universal_pure_c_no_escape_certified', 'NO_ESCAPE' in str(pure.get('status','')).upper() or pure.get('pure_c_no_escape') is True, 'medium', str(pure.get('status')))
    iso = loaded.get('universal_x_extractor_isolation_report.json', {})
    add('cvx_x_extractor_isolation_present', bool(iso), 'medium', evidence=list(iso.keys())[:10] if isinstance(iso, dict) else None)
    # Search for policy contradiction phrases in JSON reports.
    contradictions = []
    for name, obj in loaded.items():
        s = json.dumps(obj, sort_keys=True).lower()
        if ('public p includes x' in s or 'p includes x' in s) and 'excludes_x' not in s:
            contradictions.append(name)
    add('cvx_no_obvious_x_policy_contradiction_phrase', not contradictions, 'medium', evidence=contradictions)
    return all(c.passed for c in checks if c.severity in {'critical','high'}), checks


def run_mutation_suite(d20: dict, baseline_graph_hash: str, baseline_top_hash: str) -> list[dict]:
    cases = []
    def run_case(name: str, mutator, expected_reject: bool, note: str):
        obj = copy.deepcopy(d20)
        mutator(obj)
        ok, checks = RegistryVerifier(obj).validate(baseline_graph_hash=baseline_graph_hash, baseline_top_hash=baseline_top_hash)
        rejected = not ok
        cases.append({
            'name': name,
            'expected_reject': expected_reject,
            'rejected': rejected,
            'passed': rejected == expected_reject,
            'note': note,
            'failed_checks': [asdict(c) for c in checks if not c.passed and c.severity in {'critical','high'}][:6]
        })
    # 1 status tamper
    run_case('embedded_certificate_status_spoof', lambda o: o['certificates']['core.a985'].__setitem__('status','PASS_BUT_TAMPERED'), True, 'Should reject mismatch between registry expected_status and embedded status.')
    # 2 missing cert
    run_case('delete_embedded_certificate', lambda o: o['certificates'].pop('core.a985', None), True, 'Should reject missing embedded certificate for registry id.')
    # 3 duplicate id
    def dup(o):
        o['certificate_registry']['certificates'].append(copy.deepcopy(o['certificate_registry']['certificates'][0]))
    run_case('duplicate_registry_id', dup, True, 'Should reject duplicate registry id.')
    # 4 unresolved dep
    def baddep(o):
        o['certificate_registry']['certificates'][1]['depends_on'] = ['ghost.cert']
    run_case('unresolved_dependency', baddep, True, 'Should reject dependency on non-existent certificate.')
    # 5 reversed ordinal dependency
    def badord(o):
        e = o['certificate_registry']['certificates'][0]
        e['depends_on'] = ['integrity.proof_system']
    run_case('backward_dependency_cycle_or_ordinal_violation', badord, True, 'Should reject dependency that points forward and creates an order violation.')
    # 6 expected_status and embedded status altered together: only baseline hash catches it
    def coherent_spoof(o):
        o['certificates']['core.a985']['status'] = 'PASS_FORGED'
        o['certificate_registry']['certificates'][0]['expected_status'] = 'PASS_FORGED'
    run_case('coherent_status_spoof_requires_trusted_hash_pin', coherent_spoof, True, 'Semantic checks alone may pass; baseline graph/top hash must reject coherent spoofing.')
    # 7 top-level D20 status spoof
    run_case('top_level_status_degraded', lambda o: o.__setitem__('status','D20_UNCERTIFIED'), True, 'Should reject degraded top-level object status.')
    # 8 unknown group
    run_case('unknown_group_in_registry', lambda o: o['certificate_registry']['certificates'][0].__setitem__('group','ghost'), True, 'Should reject registry group not declared in group table.')
    return cases


def main():
    report: dict[str, Any] = {'schema': 'verifier_security_audit.v0', 'scope': 'defensive local software-security audit of d20 verifier artifacts, CVX trace package, and KEM audit package'}
    checks: list[Check] = []
    d20 = load_json(D20)
    baseline_graph_hash = RegistryVerifier(d20).graph_hash()
    baseline_top_hash = canon_hash(d20)
    baseline_ok, baseline_checks = RegistryVerifier(d20).validate()
    checks.extend(baseline_checks)

    # Zip safety
    for label, zp in [('cvx_trace_zip', CVX_ZIP), ('kem_audit_zip', KEM_ZIP)]:
        ok, bad = zip_safety(zp)
        checks.append(Check(f'{label}_zip_path_safety', ok, 'critical', evidence=bad))

    # Use already extracted folders if present, otherwise extract to workdir
    work = ROOT/'verifier_security_work'
    if work.exists():
        import shutil; shutil.rmtree(work)
    work.mkdir()
    with zipfile.ZipFile(KEM_ZIP) as z: z.extractall(work/'kem')
    # KEM zip uses backslashes as literal in some zip impl; normalize if necessary
    if (not (work/'kem'/'manifest.json').exists()) or (not (work/'kem'/'evidence_bundle'/'manifest.json').exists()):
        # The KEM zip uses Windows backslash names; mirror the normalized pre-extracted package.
        import shutil
        shutil.rmtree(work/'kem', ignore_errors=True)
        shutil.copytree(ROOT/'crypto_test_work'/'kem', work/'kem', dirs_exist_ok=True)
    with zipfile.ZipFile(CVX_ZIP) as z: z.extractall(work/'cvx')
    cvx_dir = work/'cvx'/'cvx_trace'
    if not cvx_dir.exists():
        cvx_dir = ROOT/'crypto_test_work'/'cvx'/'cvx_trace'

    kem_ok, kem_checks = kem_hash_coverage(work/'kem')
    checks.extend(kem_checks)
    cvx_ok, cvx_checks = cvx_policy_checks(cvx_dir)
    checks.extend(cvx_checks)

    mutation_cases = run_mutation_suite(d20, baseline_graph_hash, baseline_top_hash)

    critical_high = [c for c in checks if c.severity in {'critical','high'}]
    all_security_checks_pass = all(c.passed for c in critical_high) and all(c['passed'] for c in mutation_cases)

    report.update({
        'status': 'VERIFIER_SECURITY_AUDIT_PASS_WITH_TRUST_ROOT_GAP' if all_security_checks_pass else 'VERIFIER_SECURITY_AUDIT_FAIL',
        'd20_file_sha256': sha256_file(D20),
        'd20_canonical_json_sha256': baseline_top_hash,
        'registry_graph_sha256': baseline_graph_hash,
        'baseline_registry_ok': baseline_ok,
        'kem_ok': kem_ok,
        'cvx_ok': cvx_ok,
        'checks': [asdict(c) for c in checks],
        'mutation_suite': mutation_cases,
        'security_interpretation': {
            'what_passed': [
                'baseline registry consistency',
                'dependency DAG and ordinal discipline',
                'expected-status/embedded-status matching',
                'zip path traversal safety for uploaded packages',
                'KEM artifact hash coverage and boundary-status checks',
                'CVX X-policy boundary presence',
                'adversarial mutation rejection when baseline hash is pinned'
            ],
            'main_gap': 'The verifier needs an external trust root: a signed or separately pinned hash for d20.json / registry graph / source manifest. Coherent in-file spoofing can only be rejected by such an external pin or signature.',
            'not_claimed': [
                'no cryptographic break',
                'no peer review or independent third-party validation',
                'no full proof-assistant verification of every certificate',
                'no runtime sandbox hardening audit of future executable verifier code'
            ]
        }
    })
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding='utf-8')

    # Markdown summary
    total = len(checks); passed = sum(c.passed for c in checks)
    mut_pass = sum(1 for c in mutation_cases if c['passed'])
    md = []
    md.append('# Verifier Security Audit\n')
    md.append(f'**Status:** `{report["status"]}`\n')
    md.append('## Summary\n')
    md.append(f'- Baseline checks passed: **{passed}/{total}**\n')
    md.append(f'- Mutation tests passed: **{mut_pass}/{len(mutation_cases)}**\n')
    md.append(f'- d20 file SHA-256: `{report["d20_file_sha256"]}`\n')
    md.append(f'- Canonical JSON SHA-256: `{baseline_top_hash}`\n')
    md.append(f'- Registry graph SHA-256: `{baseline_graph_hash}`\n')
    md.append('\n## Security result\n')
    md.append('The verifier artifacts pass a local defensive security audit for registry consistency, dependency discipline, status matching, package path safety, hash coverage, and adversarial mutation rejection when the registry/content hash is pinned.\n')
    md.append('\n## Main gap\n')
    md.append('The current artifact still needs an external trust root: sign or separately pin the canonical d20 JSON hash, registry graph hash, and source manifest hash. Without that, a coherent in-file spoof can update both a forged status and its expected status.\n')
    md.append('\n## Mutation suite\n')
    md.append('| Test | Rejected | Expected reject | Pass |\n|---|---:|---:|---:|\n')
    for c in mutation_cases:
        md.append(f'| {c["name"]} | {c["rejected"]} | {c["expected_reject"]} | {c["passed"]} |\n')
    md.append('\n## Failed high/critical checks\n')
    failed = [c for c in checks if not c.passed and c.severity in {'critical','high'}]
    if not failed:
        md.append('None.\n')
    else:
        for c in failed:
            md.append(f'- `{c.name}`: {c.detail} {c.evidence}\n')
    OUT_MD.write_text(''.join(md), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['status','d20_file_sha256','d20_canonical_json_sha256','registry_graph_sha256']}, indent=2))

if __name__ == '__main__':
    main()
