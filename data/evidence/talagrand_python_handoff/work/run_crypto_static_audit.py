#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, math, os
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path('/mnt/data')
WORK = ROOT / 'crypto_test_work'
KEM = WORK / 'kem'
CVX = WORK / 'cvx' / 'cvx_trace'
OUT_JSON = ROOT / 'crypto_static_audit_report.json'
OUT_MD = ROOT / 'crypto_static_audit_report.md'


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(p: Path):
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> dict:
    if n <= 0:
        return {'lower': None, 'upper': None, 'confidence': 0.95, 'method': 'wilson'}
    phat = k / n
    denom = 1 + z*z/n
    centre = (phat + z*z/(2*n)) / denom
    half = z * math.sqrt((phat*(1-phat)+z*z/(4*n))/n) / denom
    return {'lower': max(0.0, centre-half), 'upper': min(1.0, centre+half), 'confidence': 0.95, 'method': 'wilson'}


def close(a,b,tol=5e-12):
    return abs(a-b) <= tol

report = {
    'schema': 'd20.crypto_static_audit.v0',
    'status': 'PASS',
    'limitations': [],
    'kem': {},
    'cvx_trace': {},
    'd20': {},
}

# KEM package checks
kem_manifest = load_json(KEM/'manifest.json')
kem_verif = load_json(KEM/'verification.json')
ev_manifest = load_json(KEM/'evidence_bundle'/'manifest.json')
ev_verif = load_json(KEM/'evidence_bundle'/'verification.json')
blind = load_json(KEM/'evidence_bundle'/'blind_matrix.json')
ablation = load_json(KEM/'evidence_bundle'/'ablation_ci.json')
packet = load_json(KEM/'evidence_bundle'/'packet.json')

hash_checks = {}
# wrapper output hashes
for key, path_key in [
    ('readme_sha256','readme'),
    ('replay_recipe_sha256','replay_recipe'),
    ('audit_memo_sha256','audit_memo'),
    ('verify_script_sha256','verify_script'),
    ('evidence_bundle_manifest_sha256','evidence_bundle'),
]:
    if key == 'evidence_bundle_manifest_sha256':
        expected = kem_manifest['outputs'][key]
        actual = sha256_file(KEM/'evidence_bundle'/'manifest.json')
        name = 'evidence_bundle/manifest.json'
    else:
        expected = kem_manifest['outputs'][key]
        actual = sha256_file(KEM/kem_manifest['outputs'][path_key])
        name = kem_manifest['outputs'][path_key]
    hash_checks[name] = {'expected': expected, 'actual': actual, 'ok': expected == actual}
# nested evidence hashes
for stem in ['ablation_ci_json','blind_matrix_json','packet_json','packet_markdown']:
    path = ev_manifest['outputs'][stem]
    expected = ev_manifest['outputs'][stem+'_sha256']
    actual = sha256_file(KEM/'evidence_bundle'/path)
    hash_checks['evidence_bundle/'+path] = {'expected': expected, 'actual': actual, 'ok': expected == actual}

blind_runs = blind.get('runs', [])
blind_signal_count = sum(1 for r in blind_runs if r.get('public_signal'))
blind_total = len(blind_runs)
blind_samples = sum(int(r.get('sample_count',0)) for r in blind_runs)
blind_public_events = sum(int(r.get('public_event_count',0)) for r in blind_runs)
blind_checks = {
    'run_count_36': blind_total == 36,
    'public_signal_count_0': blind_signal_count == 0,
    'sample_count_2880': blind_samples == 2880,
    'all_public_c_only': all(r.get('checks',{}).get('public_c_only_events') is True for r in blind_runs),
    'all_no_visible_or_hidden': all(r.get('checks',{}).get('no_visible_or_hidden_events_used') is True for r in blind_runs),
    'all_labels_withheld': all(r.get('checks',{}).get('challenge_labels_withheld') is True for r in blind_runs),
    'all_binary_labels': all(r.get('checks',{}).get('binary_labels') is True for r in blind_runs),
    'all_below_public_p_threshold': all((r.get('empirical_p_value',0) >= r.get('public_p_threshold',1)) and not r.get('beats_chance') for r in blind_runs),
}
blind_ci = wilson(blind_signal_count, blind_total)
blind_ci_matches = close(blind_ci['upper'], blind.get('public_signal_total',{}).get('confidence_interval',{}).get('upper', blind_ci['upper'])) if 'public_signal_total' in blind else True
# Some bundles record public_signal_total explicitly; packet and ablation do too.

mode_totals = ablation['mode_totals']
neg_totals = ablation['negative_control_totals']
recomputed_modes = {}
for mode, rec in mode_totals.items():
    k, n = int(rec['signal_count']), int(rec['total'])
    ci = wilson(k,n)
    recorded = rec['confidence_interval']
    recomputed_modes[mode] = {
        'signal_count': k, 'total': n, 'rate': k/n if n else None,
        'wilson_upper': ci['upper'], 'wilson_lower': ci['lower'],
        'recorded_upper': recorded['upper'], 'recorded_lower': recorded['lower'],
        'ci_matches': close(ci['upper'], recorded['upper']) and close(ci['lower'], recorded['lower'])
    }
recomputed_negative = {}
for mode, rec in neg_totals.items():
    k, n = int(rec['signal_count']), int(rec['total'])
    ci = wilson(k,n)
    recorded = rec['confidence_interval']
    recomputed_negative[mode] = {
        'signal_count': k, 'total': n, 'rate': k/n if n else None,
        'wilson_upper': ci['upper'], 'wilson_lower': ci['lower'],
        'recorded_upper': recorded['upper'], 'recorded_lower': recorded['lower'],
        'ci_matches': close(ci['upper'], recorded['upper']) and close(ci['lower'], recorded['lower'])
    }

ablation_checks = {
    'c_only_zero': mode_totals['C_ONLY']['signal_count'] == 0 and mode_totals['C_ONLY']['total'] == 36,
    'c_plus_v_zero': mode_totals['C_PLUS_V']['signal_count'] == 0 and mode_totals['C_PLUS_V']['total'] == 36,
    'c_plus_x_zero': mode_totals['C_PLUS_X']['signal_count'] == 0 and mode_totals['C_PLUS_X']['total'] == 36,
    'c_plus_vx_full': mode_totals['C_PLUS_VX']['signal_count'] == 36 and mode_totals['C_PLUS_VX']['total'] == 36,
    'shuffled_64_of_1152': neg_totals['VX_SHUFFLED']['signal_count'] == 64 and neg_totals['VX_SHUFFLED']['total'] == 1152,
    'aligned_lower_exceeds_shuffled_upper': ablation['separation']['aligned_lower_ci'] > ablation['separation']['shuffled_upper_ci'],
    'all_mode_ci_match': all(v['ci_matches'] for v in recomputed_modes.values()),
    'all_negative_ci_match': all(v['ci_matches'] for v in recomputed_negative.values()),
}

# Attempt official verifier; expected to fail here because tvae not installed.
import subprocess, sys
try:
    p = subprocess.run([sys.executable, '-m', 'tvae.cli', 'kem-audit-ready-verify', '--bundle', str(KEM), '--out', str(KEM/'verification_rerun.json')], capture_output=True, text=True, timeout=20)
    official = {'returncode': p.returncode, 'stdout': p.stdout[-2000:], 'stderr': p.stderr[-2000:], 'available': p.returncode == 0}
except Exception as e:
    official = {'available': False, 'error': repr(e)}
if not official.get('available'):
    report['limitations'].append('Official tvae verifier could not be rerun in this sandbox because the tvae package/repository is not installed; performed independent static and statistical consistency checks instead.')

kem_checks_bool = {}
kem_checks_bool.update({f'hash:{k}': v['ok'] for k,v in hash_checks.items()})
kem_checks_bool.update({f'blind:{k}': v for k,v in blind_checks.items()})
kem_checks_bool.update({f'ablation:{k}': v for k,v in ablation_checks.items()})
kem_checks_bool['manifest_all_checks_true'] = all(kem_manifest.get('checks',{}).values())
kem_checks_bool['packaged_verification_status_pass'] = kem_verif.get('schema') == 'tvae.kem_audit_ready_bundle_verification.v0' and all(kem_verif.get('checks',{}).values())
kem_checks_bool['nested_evidence_verification_status_pass'] = ev_verif.get('status') == 'PASS' and all(ev_verif.get('checks',{}).values())
kem_checks_bool['packet_no_break_claim'] = packet.get('checks',{}).get('no_encryption_break_claim') is True
kem_pass = all(kem_checks_bool.values())

report['kem'] = {
    'status': 'PASS' if kem_pass else 'FAIL',
    'official_verifier_attempt': official,
    'hash_checks': hash_checks,
    'checks': kem_checks_bool,
    'blind_public': {
        'status': blind.get('status'),
        'run_count': blind_total,
        'sample_count': blind_samples,
        'public_event_count': blind_public_events,
        'public_signals': blind_signal_count,
        'wilson_95': blind_ci,
        'families': sorted(set(r.get('family') for r in blind_runs)),
        'schemes': sorted(set(r.get('scheme') for r in blind_runs)),
        'implementations': sorted(set(r.get('implementation') for r in blind_runs)),
        'empirical_p_min': min(r.get('empirical_p_value',1) for r in blind_runs),
        'empirical_p_max': max(r.get('empirical_p_value',0) for r in blind_runs),
        'accuracy_min': min(r.get('accuracy',1) for r in blind_runs),
        'accuracy_max': max(r.get('accuracy',0) for r in blind_runs),
    },
    'ablation': {
        'status': ablation.get('status'),
        'modes': recomputed_modes,
        'negative_controls': recomputed_negative,
        'separation': ablation.get('separation'),
    },
    'interpretation': 'No public-only KEM signal detected in packaged blind matrix; instrumented C/V/X separation is present only when V and X are aligned. This is boundary-mechanics evidence, not an encryption break.',
}

# CVX trace checks
json_files = list(CVX.rglob('*.json'))
parse_errors = []
statuses = Counter()
claim_levels = Counter()
schemas = Counter()
for p in json_files:
    try:
        d = load_json(p)
        if isinstance(d, dict):
            if 'status' in d: statuses[d['status']] += 1
            if 'claim_level' in d: claim_levels[str(d['claim_level'])] += 1
            if 'schema' in d: schemas[str(d['schema'])] += 1
    except Exception as e:
        parse_errors.append({'path': str(p.relative_to(CVX)), 'error': repr(e)})
# schema validate selected trace/cert files
schema_validation = []
try:
    import jsonschema
    for data_path, schema_path in [
        (CVX/'traces'/'public_dpll_contradiction_4.trace.json', CVX/'schemas'/'cvx_trace.schema.json'),
        (CVX/'traces'/'cadical_lrat_contradiction_4.trace.json', CVX/'schemas'/'cvx_trace.schema.json'),
        (CVX/'certificates'/'V_VISIBLE_PUBLIC_BOUNDARY_TRANSPORT.universal_v_wall_certificate.json', CVX/'schemas'/'universal_v_wall_crossing_certificate.schema.json'),
        (CVX/'certificates'/'V_VISIBLE_COMMUTATOR_WALL_CROSSING.universal_v_wall_certificate.json', CVX/'schemas'/'universal_v_wall_crossing_certificate.schema.json'),
    ]:
        if data_path.exists() and schema_path.exists():
            data = load_json(data_path); schema = load_json(schema_path)
            try:
                jsonschema.validate(data, schema)
                schema_validation.append({'data': str(data_path.relative_to(CVX)), 'schema': str(schema_path.relative_to(CVX)), 'ok': True})
            except Exception as e:
                schema_validation.append({'data': str(data_path.relative_to(CVX)), 'schema': str(schema_path.relative_to(CVX)), 'ok': False, 'error': str(e)[:500]})
except Exception as e:
    schema_validation.append({'ok': False, 'error': 'jsonschema unavailable or validation setup failed: '+repr(e)})

# key CVX statuses
key_paths = [
    'index.json',
    'reports/x_policy_boundary_certificate.json',
    'reports/universal_x_extractor_isolation_report.json',
    'reports/universal_pure_c_no_escape_report.json',
    'reports/pure_c_no_escape_report.json',
    'reports/semantic_x_reclassification_theorem.json',
    'reports/universal_v_wall_crossing_accounting_report.json',
    'reports/p_not_np_model_scoped_theorem.json',
    'reports/standard_p_not_np_promotion_certificate.json',
    'reports/external_formal_audit_pack.json',
    'reports/t985_univalent_equivalence_obligation.json',
]
key_status = {}
for kp in key_paths:
    p = CVX/kp
    if p.exists():
        d = load_json(p)
        key_status[kp] = {k: d.get(k) for k in ['schema','status','claim_level'] if k in d}
        if 'checks' in d:
            key_status[kp]['checks_true'] = all(d['checks'].values()) if isinstance(d['checks'], dict) else None

cvx_checks_bool = {
    'all_json_parse': not parse_errors,
    'selected_schema_validations_pass': all(x.get('ok') for x in schema_validation),
    'x_policy_public_p_excludes_x': key_status.get('reports/x_policy_boundary_certificate.json',{}).get('status') == 'X_POLICY_BOUNDARY_CERTIFIED_PUBLIC_P_EXCLUDES_X',
    'universal_x_isolated': key_status.get('reports/universal_x_extractor_isolation_report.json',{}).get('status') == 'UNIVERSAL_X_EXTRACTOR_SURFACE_ISOLATION_PASS',
    'pure_c_no_escape_pass': key_status.get('reports/universal_pure_c_no_escape_report.json',{}).get('status') == 'UNIVERSAL_PURE_C_NO_ESCAPE_WITNESS_PASS',
    't985_backward_direction_blocked': key_status.get('reports/t985_univalent_equivalence_obligation.json',{}).get('status') == 'T985_UNIVALENT_EQUIVALENCE_BLOCKED_BACKWARD_DIRECTION_MISSING',
}
cvx_pass = all(cvx_checks_bool.values())
report['cvx_trace'] = {
    'status': 'PASS' if cvx_pass else 'FAIL',
    'json_file_count': len(json_files),
    'parse_errors': parse_errors,
    'schema_validation': schema_validation,
    'status_histogram': dict(statuses.most_common()),
    'claim_level_histogram': dict(claim_levels.most_common()),
    'key_status': key_status,
    'checks': cvx_checks_bool,
    'interpretation': 'C/V/X policy boundary is internally packaged: public C-only traces are kept separate from X extractor surfaces; the T985 univalent equivalence remains explicitly blocked in the backward direction.'
}

# d20 parse/hash overview
D20 = ROOT/'d20.json'
try:
    d20 = load_json(D20)
    d20_status = 'PASS'
    d20_hash = sha256_file(D20)
    cert_reg = d20.get('certificate_registry', {}) if isinstance(d20, dict) else {}
    certs = cert_reg.get('certificates', []) if isinstance(cert_reg, dict) else []
    groups = Counter(c.get('group') for c in certs if isinstance(c, dict))
    report['d20'] = {
        'status': d20_status,
        'sha256': d20_hash,
        'top_level_keys': list(d20.keys())[:50] if isinstance(d20, dict) else [],
        'certificate_registry_status': cert_reg.get('status'),
        'certificate_count': len(certs),
        'certificate_groups': dict(groups),
        'registry_policy_source_of_truth': cert_reg.get('policy',{}).get('certificate_registry_is_source_of_truth') if isinstance(cert_reg, dict) else None,
    }
except Exception as e:
    report['d20'] = {'status': 'FAIL', 'error': repr(e)}

report['status'] = 'PASS' if (kem_pass and cvx_pass and report['d20']['status']=='PASS') else 'PARTIAL_FAIL'

# write JSON
OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

# markdown
lines = []
lines.append('# Crypto Static Audit Report')
lines.append('')
lines.append(f'Overall status: **{report["status"]}**')
lines.append('')
lines.append('## KEM audit-ready bundle')
lines.append('')
lines.append(f'Status: **{report["kem"]["status"]}**')
lines.append('')
lines.append('| Test | Result |')
lines.append('|---|---:|')
lines.append(f'| Declared file-hash checks | {sum(v["ok"] for v in hash_checks.values())}/{len(hash_checks)} |')
lines.append(f'| Blind public runs | {blind_total} |')
lines.append(f'| Blind public samples | {blind_samples} |')
lines.append(f'| Blind public signals | {blind_signal_count}/{blind_total} |')
lines.append(f'| Blind public 95% Wilson upper | {blind_ci["upper"]:.9f} |')
lines.append(f'| C+V+X aligned signals | {mode_totals["C_PLUS_VX"]["signal_count"]}/{mode_totals["C_PLUS_VX"]["total"]} |')
lines.append(f'| C-only signals | {mode_totals["C_ONLY"]["signal_count"]}/{mode_totals["C_ONLY"]["total"]} |')
lines.append(f'| V-only-visible added signals (C+V) | {mode_totals["C_PLUS_V"]["signal_count"]}/{mode_totals["C_PLUS_V"]["total"]} |')
lines.append(f'| X-only-hidden added signals (C+X) | {mode_totals["C_PLUS_X"]["signal_count"]}/{mode_totals["C_PLUS_X"]["total"]} |')
lines.append(f'| Shuffled V/X control signals | {neg_totals["VX_SHUFFLED"]["signal_count"]}/{neg_totals["VX_SHUFFLED"]["total"]} |')
lines.append(f'| Aligned lower CI > shuffled upper CI | {ablation_checks["aligned_lower_exceeds_shuffled_upper"]} |')
lines.append('')
lines.append('Interpretation: no public-only leakage signal is present in the packaged blind matrix. The instrumented signal appears only when V and X are aligned, so it supports boundary-mechanics separation rather than an encryption break.')
lines.append('')
lines.append('## CVX trace package')
lines.append('')
lines.append(f'Status: **{report["cvx_trace"]["status"]}**')
lines.append('')
lines.append('| Test | Result |')
lines.append('|---|---:|')
lines.append(f'| JSON files parsed | {len(json_files)} |')
lines.append(f'| Parse errors | {len(parse_errors)} |')
lines.append(f'| Selected schema validations passed | {sum(1 for x in schema_validation if x.get("ok"))}/{len(schema_validation)} |')
for k, v in cvx_checks_bool.items():
    lines.append(f'| {k} | {v} |')
lines.append('')
lines.append('Key CVX statuses:')
lines.append('')
lines.append('| Artifact | Status | Claim level |')
lines.append('|---|---|---|')
for kp, ks in key_status.items():
    lines.append(f'| `{kp}` | `{ks.get("status", "")}` | `{ks.get("claim_level", "")}` |')
lines.append('')
lines.append('## d20 registry')
lines.append('')
lines.append(f'd20 parse status: **{report["d20"]["status"]}**')
lines.append(f'd20 SHA-256: `{report["d20"].get("sha256", "")}`')
lines.append(f'Certificate registry status: `{report["d20"].get("certificate_registry_status", "")}`')
lines.append(f'Certificate count: `{report["d20"].get("certificate_count", "")}`')
lines.append('')
lines.append('## Limitations')
lines.append('')
for lim in report['limitations']:
    lines.append(f'- {lim}')
lines.append('- This audit did not rebuild liboqs/PQClean/HQC, regenerate KEM traces, or perform cryptanalysis. It validates the uploaded package and recomputes its advertised statistical separation checks.')
lines.append('')
OUT_MD.write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(OUT_JSON)
print(OUT_MD)
print(report['status'])
