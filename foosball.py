# This file contains the core functionality of the foosball simulation
logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')

def getplayersbeside(king):
    p=[]
    for x in PLAYER_LIST:
        if x != king:
            p.append(x)
    return p

def generate_game(pa,pb,stats):
    #ee=elo_expected(stats['players'][pa]['elo'],stats['players'][pb]['elo'])
    #rr=random.random()
    #game=['','','']
    # Average of points scored and points allowed
    lambda_a = (stats['players'][pa]['ps/g'] + stats['players'][pb]['pa/g']) / 2.0
    lambda_b = (stats['players'][pb]['ps/g'] + stats['players'][pa]['pa/g']) / 2.0
    oldking=stats['overall']['king']
    ot=False
    sa=poisson_sample(lambda_a)
    sb=poisson_sample(lambda_b)
    if sa>sb:
        winner=pa
        loser=pb
    elif sa<sb:
        winner=pb
        loser=pa
    else:
        # TIEBREAK
        ot=True
        if random.random() * (lambda_a + lambda_b) < lambda_a:
            winner=pa
            loser=pb
            sa += 1
        else:
            winner=pb
            loser=pa
            sb += 1
    if loser == oldking:
        newking=winner
    else:
        newking=oldking
    # print "game generator"
    ec=elo_change(stats['players'][winner]['elo'],stats['players'][loser]['elo'],sa,sb)

    return {'p1':{'name':pa,'score':sa},'p2':{'name':pb,'score':sb},'ot':False,'winner':winner,'loser':loser,'ec':ec,'ot':ot,'king':{'old':oldking,'new':newking}}


def game_test(numgames,base_stats):
    test_stats=copy.deepcopy(base_stats)
    print(stat_report(test_stats))
    grs=[]
    start_time = time.time()
    for x in range(numgames):
        # if x % 1000000 == 0:
        #     now_time = time.time()
        #     slack_say(str(x) + ' games completed in ' + str(now_time-start_time) + ' seconds. ETR: ' + str((x/float(numgames)/)
        pab = random.sample(PLAYER_LIST,2)
        game = generate_game(pab[0],pab[1],test_stats)
        playerscores={'price':'','tritz':'','elliott':''}
        playerscores[game['p1']['name']] = str(game['p1']['score'])
        playerscores[game['p2']['name']] = str(game['p2']['score'])
        statsformatgame=[str(x+1),'XX-XX-XXXX',playerscores['price'],playerscores['tritz'],playerscores['elliott']]
        gamerecord=update_stats(statsformatgame,test_stats)
        grs.append(list(gamerecord[0]))
    with open(WORKING_DIR + 'simresults.csv','w') as sim_results_csv:
        rwriter=csv.writer(sim_results_csv)
        for gamerecord in grs:
            rwriter.writerow(list(gamerecord))
    slack_stats_report(test_stats)

if FIRST_RUN:
    foos_json = starting_stats()
    og_results_csv = open(WORKING_DIR + 'original_results.csv')
    ogreader = csv.reader(og_results_csv)
    og_results = list(ogreader)

    with open(WORKING_DIR + 'results.csv','w') as new_results_csv:
        rwriter=csv.writer(new_results_csv)

        for gamenum in range(1,len(og_results)):
            td=datetime.timedelta(days=int(og_results[gamenum][1])-1)
            dt=datetime.datetime(1900,1,1)+td
            dts=str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)
            og_results[gamenum][1] = dts
            gr = update_stats(og_results[gamenum],foos_json)
            rwriter.writerow(list(gr[0]))

    slack_stats_report(foos_json)
    with open(WORKING_DIR + 'current_standings.json','w') as standings_file:
        standings_file.write(json.dumps(foos_json,indent=4))

if TEST_MODE:
    # elo_test(10)

    game_test(100,foos_json)


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
    print vgame_report(g2_result,foos_json)
    playerscores[g2_result['p1']['name']] = str(g2_result['p1']['score'])
    playerscores[g2_result['p2']['name']] = str(g2_result['p2']['score'])
    statsformatgame=[str(rgnum),dts,playerscores['price'],playerscores['tritz'],playerscores['elliott']]
    rgnum+=1
    gamerecord=update_stats(statsformatgame,foos_json)
    results.append(gamerecord[0])
    slack_game_report(g2_result,foos_json,rgnum-1,gamerecord[2],gamerecord[3])
    print stat_report(foos_json)

    playerscores={'price':'','tritz':'','elliott':''}
    g3_result=generate_game(g1_result['loser'],king,foos_json)
    slack_game_start(rgnum,[g1_result['loser'],king],foos_json)
    time.sleep(delay)
    print vgame_report(g3_result,foos_json)
    playerscores[g3_result['p1']['name']] = str(g3_result['p1']['score'])
    playerscores[g3_result['p2']['name']] = str(g3_result['p2']['score'])
    statsformatgame=[str(rgnum),dts,playerscores['price'],playerscores['tritz'],playerscores['elliott']]
    gamerecord=update_stats(statsformatgame,foos_json)
    results.append(gamerecord[0])
    slack_game_report(g3_result,foos_json,rgnum,gamerecord[2],gamerecord[3])
    print stat_report(foos_json)

    slack_stats_report(foos_json)

    with open(WORKING_DIR + 'current_standings.json','w') as standings_file:
        standings_file.write(json.dumps(foos_json,indent=4))

    with open(WORKING_DIR + 'results.csv','w') as new_results_csv:
        rwriter=csv.writer(new_results_csv)
        rwriter.writerows(results)