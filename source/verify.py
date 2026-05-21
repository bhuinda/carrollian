from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnat import golay,tensor,quotients,packet20,h_cycle,sixj,co1,hamiltonian,certificate,deepcheck

TASKS={
    'golay': lambda: golay.verify(),
    'tensor': lambda: tensor.verify(ROOT),
    'quotients': lambda: quotients.verify(ROOT),
    'packet20': lambda: packet20.verify(ROOT),
    'h-cycle': lambda: h_cycle.verify(ROOT),
    'sixj': lambda: sixj.verify(),
    'co1': lambda: co1.verify(ROOT),
    'hamiltonian': lambda: hamiltonian.verify(ROOT),
    'deepcheck': lambda: deepcheck.verify_payload(certificate.build(ROOT)),
}

def json_text(obj, pretty=False):
    return json.dumps(obj, sort_keys=True, indent=(2 if pretty else None), separators=((',', ': ') if pretty else (',',':')), ensure_ascii=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode', nargs='?', default='generate', choices=['generate','certificate','verify','all']+list(TASKS))
    ap.add_argument('--pretty', action='store_true')
    ap.add_argument('--pass-only', action='store_true')
    ap.add_argument('--out', type=str, default=None, help='write JSON output to this path')
    ap.add_argument('--quiet', action='store_true', help='do not print JSON when --out is used')
    args=ap.parse_args()

    if args.mode in {'generate','certificate'}:
        out=certificate.build(ROOT)
    elif args.mode=='verify':
        certificate.build(ROOT)
        out={'status':'PASS'}
    elif args.mode=='all':
        out={k:f() for k,f in TASKS.items()}
    else:
        out={args.mode:TASKS[args.mode]()}

    if args.out:
        Path(args.out).write_text(json_text(out,args.pretty)+'\n',encoding='utf-8')

    if args.pass_only or args.mode=='verify':
        print('PASS')
    elif not (args.out and args.quiet):
        print(json_text(out,args.pretty))

if __name__=='__main__': main()
