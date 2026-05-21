from fractions import Fraction
from collections import Counter
from .packet20 import C20

def verify(root):
    C=C20(root)
    row=[sum(r) for r in C]
    assert row==[90,264,225,65,99,66]
    pi_num=[29400,37840,21375,31460,37840,34848]; pi_den=192763
    for j in range(6):
        lhs=sum(Fraction(pi_num[i],pi_den)*Fraction(C[i][j],row[i]) for i in range(6))
        assert lhs==Fraction(pi_num[j],pi_den)
    J=[[Fraction(pi_num[i],pi_den)*Fraction(C[i][j],row[i])-Fraction(pi_num[j],pi_den)*Fraction(C[j][i],row[j]) for j in range(6)] for i in range(6)]
    assert all(sum(r)==0 for r in J)
    TV=sum(abs(J[i][j]) for i in range(6) for j in range(6))/2
    ratios=[]
    for i in range(6):
        for j in range(6):
            for k in range(6):
                if len({i,j,k})==3:
                    ratios.append(Fraction(C[i][j],row[i])*Fraction(C[j][k],row[j])*Fraction(C[k][i],row[k])/(Fraction(C[j][i],row[j])*Fraction(C[k][j],row[k])*Fraction(C[i][k],row[i])))
    cnt=Counter(ratios)
    assert dict(cnt)=={Fraction(1,4):3,Fraction(1,2):30,Fraction(1,1):54,Fraction(2,1):30,Fraction(4,1):3}
    return {'row_sums':row,'stationary_pi':[pi_num,pi_den],'current_total_variation':[TV.numerator,TV.denominator],'triangle_ratio_counts':{str(k):v for k,v in sorted(cnt.items(), key=lambda x: float(x[0]))}}
