import math

def verify():
    F=[[1/3,-math.sqrt(3)/3,math.sqrt(5)/3],[-math.sqrt(3)/3,1/2,math.sqrt(15)/6],[math.sqrt(5)/3,math.sqrt(15)/6,1/6]]
    err=0.0
    for i in range(3):
        for j in range(3):
            err=max(err,abs(sum(F[k][i]*F[k][j] for k in range(3))-(1.0 if i==j else 0.0)))
    det=F[0][0]*(F[1][1]*F[2][2]-F[1][2]*F[2][1])-F[0][1]*(F[1][0]*F[2][2]-F[1][2]*F[2][0])+F[0][2]*(F[1][0]*F[2][1]-F[1][1]*F[2][0])
    assert err<1e-12 and abs(det+1)<1e-12 and abs(F[1][1]-0.5)<1e-12
    return {'sixj': '1/6', 'associator': '1/2', 'orthogonality_error': err, 'determinant': det}
