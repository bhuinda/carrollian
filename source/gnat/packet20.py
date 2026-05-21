from pathlib import Path
from fractions import Fraction
import json
from .exact import rank, matmul, transpose, det_bareiss_int, pfaffian_6, to_frac_matrix, eye, outer, sub, vecmul, rowmul

def C20(root): return json.load(open(Path(root)/'data'/'constants.json'))['packet20']['C20']

def verify(root):
    C=C20(root)
    assert C==[[6,12,12,24,12,24],[48,48,24,48,48,48],[32,64,1,32,64,32],[16,16,8,1,16,8],[9,18,18,18,18,18],[12,12,6,12,12,12]]
    assert rank(C)==5
    ell=[0,1,0,0,-1,0]; eta=[0,1,0,0,0,-4]
    F=lambda xs: list(map(Fraction,xs))
    Cf=to_frac_matrix(C)
    assert vecmul(Cf,F(ell))==[0]*6
    assert rowmul(F(eta),Cf)==[0]*6
    assert sum(eta[i]*ell[i] for i in range(6))==1
    P=sub(eye(6),outer(F(ell),F(eta)))
    assert matmul(P,P)==P
    assert matmul(matmul(P,Cf),P)==Cf
    q=matmul(transpose(Cf),Cf)
    N=[[C[i][j]-C[j][i] for j in range(6)] for i in range(6)]
    pf=pfaffian_6(N)
    stretched=[[int(q[i][j])+eta[i]*eta[j] for j in range(6)] for i in range(6)]
    det1=det_bareiss_int(stretched)
    assert rank(q)==5 and rank(N)==6 and pf==-8688 and det1==5553107788032
    return {'rank_C20':5,'right_null':ell,'left_null':eta,'rank_CtC':5,'rank_skew':6,'pfaffian_skew':int(pf),'det_stretched':det1}
