from foos_config import ELO_N, ELO_K
import logging

logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')

def elo_expected(ratingA, ratingB):
    qa=10.0**(ratingA/ELO_N)
    logging.debug('QA: ' + str(qa))
    qb=10.0**(ratingB/ELO_N)
    logging.debug('QB: ' + str(qb))
    expectedA=qa/(qa+qb)
    logging.debug('EA: ' + str(expectedA))
    expectedB=qb/(qa+qb)
    logging.debug('EB: ' + str(expectedB))
    return (expectedA, expectedB)

def elo_change(ratingA,ratingB,scoreA,scoreB):
    expected = elo_expected(ratingA,ratingB)
    if scoreA > scoreB:
        playerAwin=True
    else:
        playerAwin=False
    if playerAwin:
        logging.debug('Result: A [' + str(ratingA) + '] beats B [' + str(ratingB) + '] ' + str(scoreA) + '-' + str(scoreB))
        actual=1.0
    else:
        logging.info('Result: B [' + str(ratingB) + '] beats A [' + str(ratingA) + '] ' + str(scoreB) + '-' + str(scoreA))
        actual=0.0
    delta = ELO_K*(actual - expected[0])
    logging.debug('Delta: ' + str(delta))
    new_ratingA = ratingA + delta
    logging.info('ratingA: ' + str(ratingA) + '-->' + str(new_ratingA))
    new_ratingB = ratingB - delta
    logging.info('ratingB: ' + str(ratingB) + '-->' + str(new_ratingB))
    return (new_ratingA, new_ratingB, delta)

