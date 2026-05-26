from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
EXPECTED_COUNTS={12:2576,16:759}
def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''):
            h.update(chunk)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--out', default='out_validate'); args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    df=pd.read_csv(args.csv)
    failures=[]; summary=[]
    for shell,sub in df.groupby('shell'):
        shell=int(shell); L=(shell+1)**2
        for idx,row in sub.iterrows():
            arr=np.fromstring(row['profile'], sep=',', dtype=np.int64)
            ok_len=len(arr)==L; ok_sum=int(arr.sum())==EXPECTED_COUNTS[shell]
            mat=arr.reshape((shell+1,shell+1)); j=np.arange(shell+1)[:,None]; k=np.arange(shell+1)[None,:]
            den=EXPECTED_COUNTS[shell]*shell
            first_num=int((mat*j).sum()); second_num=int((mat*k).sum())
            ok_int=(24*first_num)%den==0 and (24*second_num)%den==0
            first=(24*first_num)//den if ok_int else -1; second=(24*second_num)//den if ok_int else -1
            ok_mom=ok_int and first==int(row['first_size']) and second==int(row['second_size']) and first+second+int(row['rest_size'])==24
            if not(ok_len and ok_sum and ok_mom): failures.append({'row':int(idx),'shell':shell,'ok_len':ok_len,'ok_sum':ok_sum,'ok_mom':ok_mom})
        summary.append({'shell':shell,'rows':int(len(sub)),'expected_rows':4612,'profile_length':L,'unique_profile_sha256':int(sub['profile_sha256'].nunique()),'profile_ids_contiguous': sorted(sub['profile_id'].tolist())==list(range(len(sub)))})
    report={'status':'PASS' if not failures else 'FAIL','csv_sha256':sha256_file(Path(args.csv)),'total_rows':int(len(df)),'summary':summary,'failure_count':len(failures),'failures_first_50':failures[:50]}
    (out/'validation_report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__': main()
