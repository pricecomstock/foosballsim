# This file contains all the stats logic
import logging
from elo import elo_change

logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')

def update_stats(game,sjson):
    gameseq=int(game[0])
    gamedate=game[1]
    scores={'price':game[2],'tritz':game[3],'elliott':game[4]}
    for player in scores:
        if scores[player] == '':
            manout=player
        elif scores[player] == max(scores.values(),key=blanksafeint):
            wscore=float(scores[player])
            winner=player
        else:
            lscore=float(scores[player])
            loser=player


    ##################
    # Streak
    # winner
    if sjson['players'][winner]['streak']['type'] == 'W':
        sjson['players'][winner]['streak']['length'] += 1
    else:
        sjson['players'][winner]['streak']['type'] = 'W'
        sjson['players'][winner]['streak']['length'] = 1

    # loser
    if sjson['players'][loser]['streak']['type'] == 'L':
        sjson['players'][loser]['streak']['length'] += 1
    else:
        sjson['players'][loser]['streak']['type'] = 'L'
        sjson['players'][loser]['streak']['length'] = 1

    ##################
    # PS/G
    if sjson['players'][winner]['ps/g'] >= 0:
        sjson['players'][winner]['ps/g'] = (sjson['players'][winner]['games'] * sjson['players'][winner]['ps/g'] + wscore)/(sjson['players'][winner]['games'] + 1)
    else:
        sjson['players'][winner]['ps/g'] = wscore

    if sjson['players'][loser]['ps/g'] >= 0:
        sjson['players'][loser]['ps/g'] = (sjson['players'][loser]['games'] * sjson['players'][loser]['ps/g'] + lscore)/(sjson['players'][loser]['games'] + 1)
    else:
        sjson['players'][loser]['ps/g'] = lscore

    ##################
    # PA/G
    if sjson['players'][winner]['pa/g'] >= 0:
        sjson['players'][winner]['pa/g'] = (sjson['players'][winner]['games'] * sjson['players'][winner]['pa/g'] + lscore)/(sjson['players'][winner]['games'] + 1)
    else:
        sjson['players'][winner]['pa/g'] = lscore

    if sjson['players'][loser]['pa/g'] >= 0:
        sjson['players'][loser]['pa/g'] = (sjson['players'][loser]['games'] * sjson['players'][loser]['pa/g'] + wscore)/(sjson['players'][loser]['games'] + 1)
    else:
        sjson['players'][loser]['pa/g'] = wscore

    ##################
    # Avg Margin Victory
    if sjson['players'][winner]['am+'] >= 0:
        sjson['players'][winner]['am+'] = (sjson['players'][winner]['wins'] * sjson['players'][winner]['am+'] + (wscore-lscore))/(sjson['players'][winner]['wins'] + 1)
    else:
        sjson['players'][winner]['am+'] = wscore - lscore

    ##################
    # Avg Margin Loss
    if sjson['players'][loser]['am-'] >= 0:
        sjson['players'][loser]['am-'] = (sjson['players'][loser]['losses'] * sjson['players'][loser]['am-'] + (wscore-lscore))/(sjson['players'][loser]['losses'] + 1)
    else:
        sjson['players'][loser]['am-'] = wscore - lscore

    ##################
    # King
    if loser == sjson['overall']['king'] or sjson['overall']['king'] == '':
        sjson['overall']['king'] = winner
        king_s='NEW KING'
    else:
        king_s=''

    ##################
    # Elo
    # print "stats updater"
    ec = elo_change(sjson['players'][winner]['elo'],sjson['players'][loser]['elo'],wscore,lscore)
    wes="[" + "{0:.1f}".format(sjson['players'][winner]['elo']) + "-->" + "{0:.1f}".format(ec[0]) + ' | +' + "{0:.1f}".format(ec[2]) + "]"
    les="[" + "{0:.1f}".format(sjson['players'][loser]['elo']) + "-->" + "{0:.1f}".format(ec[1]) + ' | -' + "{0:.1f}".format(ec[2]) + "]"
    sjson['players'][winner]['elo'] = ec[0]
    sjson['players'][loser]['elo'] = ec[1]


    ##################
    # Wins + games
    sjson['players'][winner]['games'] += 1
    sjson['players'][winner]['wins'] += 1

    ##################
    # Losses + games
    sjson['players'][loser]['games'] += 1
    sjson['players'][loser]['losses'] += 1

    ##################
    # Win Percent
    sjson['players'][winner]['winpct'] = float(sjson['players'][winner]['wins'])/float(sjson['players'][winner]['games'])
    sjson['players'][loser]['winpct'] = float(sjson['players'][loser]['wins'])/float(sjson['players'][loser]['games'])

    game_summary='GAME #' +str(gameseq) + ': ' + winner + ' ' + wes + ' defeats ' + loser + ' ' + les + ' ' + king_s
    logging.debug(game_summary)
    return ((gameseq,gamedate,game[2],game[3],game[4],sjson['players']['price']['elo'],sjson['players']['tritz']['elo'],sjson['players']['elliott']['elo']),game_summary,wes,les)