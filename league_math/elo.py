from foos_config import ELO_N, ELO_K

def elo_expected(ratingA, ratingB):
    qa=10.0**(ratingA/ELO_N)
    qb=10.0**(ratingB/ELO_N)
    
    expectedA=qa/(qa+qb)
    expectedB=qb/(qa+qb)
    
    return (expectedA, expectedB)

def elo_change(ratingA,ratingB,scoreA,scoreB):
    expected = elo_expected(ratingA,ratingB)
    
    if scoreA > scoreB:
        playerAwin=True
    else:
        playerAwin=False
    
    if playerAwin:
        actual=1.0
    else:
        actual=0.0
    
    delta = ELO_K*(actual - expected[0])
    new_ratingA = ratingA + delta
    new_ratingB = ratingB - delta
    
    return (new_ratingA, new_ratingB, delta)