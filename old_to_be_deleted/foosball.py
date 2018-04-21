import logging
from foos_config import PLAYER_LIST
from poisson import poisson_sample
import random
from elo import elo_change
import copy
import time

# This file contains the core functionality of the foosball simulation
logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')

def getplayersbeside(king):
    p=[]
    for x in PLAYER_LIST:
        if x != king:
            p.append(x)
    return p

def generate_game(player_a,player_b,stats):
    # Average of points scored and points allowed
    lambda_a = (stats['players'][player_a]['ps/g'] + stats['players'][player_b]['pa/g']) / 2.0
    lambda_b = (stats['players'][player_b]['ps/g'] + stats['players'][player_a]['pa/g']) / 2.0
    
    oldking=stats['overall']['king']
    overtime=False
    score_a=poisson_sample(lambda_a)
    score_b=poisson_sample(lambda_b)
    if score_a>score_b:
        winner=player_a
        loser=player_b
    elif score_a<score_b:
        winner=player_b
        loser=player_a
    else:
        # TIEBREAK
        overtime=True
        if random.random() * (lambda_a + lambda_b) < lambda_a:
            winner=player_a
            loser=player_b
            score_a += 1
        else:
            winner=player_b
            loser=player_a
            score_b += 1
    if loser == oldking:
        newking=winner
    else:
        newking=oldking
    # print "game generator"
    ec=elo_change(stats['players'][winner]['elo'],stats['players'][loser]['elo'],score_a,score_b)

    return {'p1':{'name':player_a,'score':score_a},'p2':{'name':player_b,'score':score_b},'winner':winner,'loser':loser,'ec':ec,'ot':overtime,'king':{'old':oldking,'new':newking}}

def bo3():
    king=foos_json['overall']['king']
    g1_players=getplayersbeside(king)
    with open(WORKING_DIR + 'results.csv') as results_csv:
        reader = csv.reader(results_csv)
        results = list(reader)

    delay=300

    rgnum = int(results[-1][0]) + 1

    dt=datetime.datetime.now()
    dts=str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)

    playerscores={'price':'','tritz':'','elliott':''}
    slack_game_start(rgnum,g1_players,foos_json)
    time.sleep(delay)
    g1_result=generate_game(g1_players[0],g1_players[1],foos_json)
    print(vgame_report(g1_result,foos_json))
    playerscores[g1_result['p1']['name']] = str(g1_result['p1']['score'])
    playerscores[g1_result['p2']['name']] = str(g1_result['p2']['score'])
    statsformatgame=[str(rgnum),dts,playerscores['price'],playerscores['tritz'],playerscores['elliott']]
    rgnum+=1
    gamerecord=update_stats(statsformatgame,foos_json)
    results.append(gamerecord[0])
    slack_game_report(g1_result,foos_json,rgnum-1,gamerecord[2],gamerecord[3])
    print(stat_report(foos_json))

    playerscores={'price':'','tritz':'','elliott':''}
    g2_result=generate_game(g1_result['winner'],king,foos_json)
    slack_game_start(rgnum,[g1_result['winner'],king],foos_json)
    time.sleep(delay)
    print(vgame_report(g2_result,foos_json))
    playerscores[g2_result['p1']['name']] = str(g2_result['p1']['score'])
    playerscores[g2_result['p2']['name']] = str(g2_result['p2']['score'])
    statsformatgame=[str(rgnum),dts,playerscores['price'],playerscores['tritz'],playerscores['elliott']]
    rgnum+=1
    gamerecord=update_stats(statsformatgame,foos_json)
    results.append(gamerecord[0])
    slack_game_report(g2_result,foos_json,rgnum-1,gamerecord[2],gamerecord[3])
    print(stat_report(foos_json))

    playerscores={'price':'','tritz':'','elliott':''}
    g3_result=generate_game(g1_result['loser'],king,foos_json)
    slack_game_start(rgnum,[g1_result['loser'],king],foos_json)
    time.sleep(delay)
    print(vgame_report(g3_result,foos_json))
    playerscores[g3_result['p1']['name']] = str(g3_result['p1']['score'])
    playerscores[g3_result['p2']['name']] = str(g3_result['p2']['score'])
    statsformatgame=[str(rgnum),dts,playerscores['price'],playerscores['tritz'],playerscores['elliott']]
    gamerecord=update_stats(statsformatgame,foos_json)
    results.append(gamerecord[0])
    slack_game_report(g3_result,foos_json,rgnum,gamerecord[2],gamerecord[3])
    print(stat_report(foos_json))

    slack_stats_report(foos_json)

    with open(WORKING_DIR + 'current_standings.json','w') as standings_file:
        standings_file.write(json.dumps(foos_json,indent=4))

    with open(WORKING_DIR + 'results.csv','w') as new_results_csv:
        rwriter=csv.writer(new_results_csv)
        rwriter.writerows(results)