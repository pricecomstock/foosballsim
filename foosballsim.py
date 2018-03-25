import time
import csv
import random
import json
import logging
import copy
import requests
import math
import datetime
import pandas as pd

day=datetime.datetime.today().weekday()
if day not in [0,1,2,3,4]:
    exit(0)

logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')

ELO_K=50.0
ELO_N=290.0
FIRST_RUN = False
TEST_MODE = False
GAME_MODE = True
CHART_MODE = False
SIMULATION_MODE = False
WORKING_DIR = '/home/pricecomstock/slash-selfie/foosball/'
PLAYER_LIST = ['price','tritz','elliott']
WEBHOOK_URL = 'https://hooks.slack.com/services/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'
with open(WORKING_DIR + 'current_standings.json') as standings_file:
    foos_json = json.load(standings_file)

def getplayersbeside(king):
    p=[]
    for x in PLAYER_LIST:
        if x != king:
            p.append(x)
    return p

def blanksafeint(s):
    if s != '':
        return int(s)
    else:
        return None

def game_report(game,sjson):
    report=''
    #"{0:.1f}".format(game[])
    report += game['p1']['name'].rjust(10) + ' ' + str(game['p1']['score']).rjust(3)
    report += ' | '
    report += str(game['p2']['score']).ljust(3)  + ' ' + game['p2']['name'].ljust(10)
    print(report)
    return report

def vgame_report(game,sjson):
    report=''
    #"{0:.1f}".format(game[])
    report += '\n'
    report += game['p1']['name'].rjust(10) + ' ' + str(game['p1']['score']).ljust(3) +'+'*game['p1']['score']
    report += '\n'
    report += game['p2']['name'].rjust(10) + ' ' + str(game['p2']['score']).ljust(3) +'+'*game['p2']['score']
    return report

def stat_report(sjson):
    report = ''
    WL_just = 4
    for x in range(11,3,-1):
        if sjson['players']['tritz']['wins'] / (10**(x-1)) > 0:
            WL_just=x + 1
            break

    report += ''.join([
        'PLAYER'.ljust(8) + '|',
        'W'.rjust(WL_just),
        'L'.rjust(WL_just),
        'RUN'.rjust(4),
        'PS/G'.rjust(6),
        'PA/G'.rjust(6),
        'AM+'.rjust(6),
        'AM-'.rjust(6),
        'WIN%'.rjust(7),
        'ELO'.rjust(7),
        'KING'.rjust(5)
        ])
    report += '\n'+'='*len(report)
    eloranks=[('price',sjson['players']['price']['elo']),('tritz',sjson['players']['tritz']['elo']),('elliott',sjson['players']['elliott']['elo'])]
    eloranks.sort(key=lambda tup: tup[1],reverse=True)
    for player in eloranks:
        psl=sjson['players'][player[0]]
        king_string = ''
        if sjson['overall']['king'] == player[0]:
            king_string = ' K'
        report += '\n' + ''.join([
            player[0].ljust(8) + '|',
            str(psl['wins']).rjust(WL_just),
            str(psl['losses']).rjust(WL_just),
            (str(psl['streak']['length'])+psl['streak']['type']).rjust(4),
            "{0:.2f}".format(psl['ps/g']).rjust(6),
            "{0:.2f}".format(psl['pa/g']).rjust(6),
            "{0:.2f}".format(psl['am+']).rjust(6),
            "{0:.2f}".format(psl['am-']).rjust(6),
            "{0:.3f}".format(psl['winpct']).rjust(7),
            "{0:.1f}".format(psl['elo']).rjust(7),
            king_string
            ])

    return report

def poisson(lambd,k):
    e=2.71828
    return ((lambd**k)*(e**(0.0-lambd)))/math.factorial(k)

def poisson_sample(lambd):
    thresh = random.random()
    p=0.0
    for x in range(25):
        p += poisson(lambd,x)
        if p >= thresh:
            return x

def slack_game_report(game,stats,gnum,wes,les):
    #return {'p1':{'name':pa,'score':sa},'p2':{'name':pb,'score':sb},'ot':False,'winner':winner,'loser':loser,'ec':ec,'ot':ot,'king':{'old':oldking,'new':newking}}
    colors={'price':'#8888BB','tritz':'#DD8888','elliott':'#88BB88'}
    king = game['king']['old']
    report='GAME #' + str(gnum) + ': '
    if game['winner'] == king:
        report += 'King '
    report += '*' + game['winner'].title() + '*'
    report += ' defeats '
    if game['loser'] == king:
        report += 'King '
        end_king=' to become King'
    else:
        end_king=''
    report += '*' + game['loser'].title() + '* '
    if game['p1']['score'] > game['p2']['score']:
        report += str(game['p1']['score']) + '-' + str(game['p2']['score'])
        es1=wes
        es2=les
    else:
        report += str(game['p2']['score']) + '-' + str(game['p1']['score'])
        es2=wes
        es1=les
    logging.info('P1E: ' + es1 + 'P2E: ' + es2)
    if game['ot']:
        report += ' in sudden death'
    report+=end_king
    report += '!'
    payload = json.dumps({
        'text':report,
        'attachments':[
            {
                'color':colors[game['winner']],
                'fallback': report,
                'fields':[
                    {
                        'title':str(game['p1']['score']) + ' - ' + game['p1']['name'] + ' ' + es1,
                        'value':':soccer:'*game['p1']['score'],
                        'short':False
                    },
                    {
                        'title':str(game['p2']['score']) + ' - ' + game['p2']['name'] + ' ' + es2,
                        'value':':soccer:'*game['p2']['score'],
                        'short':False
                    }
                ]
            }
        ]
    })
    r=requests.post(WEBHOOK_URL,data=payload)

def slack_say(s):
    payload = json.dumps({'text':s})
    requests.post(WEBHOOK_URL,data=payload)

def slack_stats_report(sjson):
    sr=stat_report(sjson)
    fsr='*STATS REPORT:*\n```'+sr+'```'
    payload = json.dumps({'text':fsr})
    r=requests.post(WEBHOOK_URL,data=payload)

def slack_game_start(gnum,participants,sjson):
    gsr=''
    curking=sjson['overall']['king']
    if curking == participants[0]:
        p1s = ' King *' + participants[0].title() + '* '
        p2s = ' *' + participants[1].title() + '* '
    elif curking == participants[1]:
        p2s = ' King *' + participants[1].title() + '* '
        p1s = ' *' + participants[0].title() + '* '
    else:
        p1s = ' *' + participants[0].title() + '* '
        p2s = ' *' + participants[1].title() + '* '

    p1s += ' [' + "{0:.1f}".format(sjson['players'][participants[0]]['elo']) + '] '
    p2s += ' [' + "{0:.1f}".format(sjson['players'][participants[1]]['elo']) + '] '

    gsr+='*UP NEXT:* game #' + str(gnum) + ':' + p1s + 'v.' + p2s
    payload = json.dumps({'text':gsr})
    r=requests.post(WEBHOOK_URL,data=payload)

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

if GAME_MODE:
    bo3()

# def point_total_chart(pt,mode='real'):
#     ptct = [[0]*25]
#     ptct_bygame = []
#     traces=[]
#     gamenums = range(1,len(pt)+1)
#     colors={'price':'#8888BB','tritz':'#DD8888','elliott':'#88BB88'}

#     for g in range(len(pt)):
#         for lindex in range(len(ptct)):
#             if lindex = pt[g]:
#                 ptct[lindex].append(ptct[-1]+1)
#             else:
#                 ptct[lindex].append(ptct[-1])
#         ptct[g][pt[g]] += 1
#         ptct_bygame.append(ptct[g])

#     for ct in ptct:
#         traces.append(
#             go.Scatter(
#                 x = gamenums,
#                 y = e[p],
#                 name = p.title(),
#                 line = dict(color=colors[p], width = 4)
#             )
#         )

#     # simple line chart
#     #layout = dict(title='Elo', xaxis = dict(title = 'Game Number'), yaxis = dict(title = 'Elo rating'))

#     layout = dict(
#     title='Time series with range slider and selectors',
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=30,
#                     label='Last 30'),
#                 dict(count=100,
#                     label='Last 100'),
#                 dict(count=len(e['price'])-471,
#                     label='Bots only'),
#                 dict(step='all',
#                     label='All')
#                 ])
#             ),
#             rangeslider=dict()
#         )
#     )

def points_violin_chart(pt,mode='real'):
    pt_samples=[]
    corr_players=[]
    colors={'price':'#8888BB','tritz':'#DD8888','elliott':'#88BB88'}

    for p in pt:
        for pgpt in pt[p]:
            pt_samples.append(pgpt)
            corr_players.append(p)

    df=pd.DataFrame(dict(Points=pt_samples,Player=corr_players))

    fig = FF.create_violin(df,data_header='Points', group_header = 'Player',colors=colors,use_colorscale=False,height=800,width=1200)

    if mode == 'real':
        fn='pt_violin'
    else:
        fn='Sim_pt_violin'
    ploturl=py.plot(fig,filename=fn)

    return ploturl

def elo_violin_chart(e,mode='real'):
    #intified = {'price':[],'tritz':[],'elliott':[]}
    #gamenums = range(1,len(e['price'])+1)
    # po=['price','tritz','elliott']
    elo_samples=[]
    corr_players=[]
    colors={'price':'#8888BB','tritz':'#DD8888','elliott':'#88BB88'}

    for p in e:
        last = -1
        for pgelo in e[p]:
            if pgelo != last:
                elo_samples.append(pgelo)
                corr_players.append(p)
                last = pgelo

    df=pd.DataFrame(dict(Elo=elo_samples,Player=corr_players))

    fig = FF.create_violin(df,data_header='Elo', group_header = 'Player',colors=colors,use_colorscale=False,height=800,width=1200)

    if mode == 'real':
        fn='elo_violin'
    else:
        fn='Sim_elo_violin'
    ploturl=py.plot(fig,filename=fn)

    return ploturl

def elo_chart(e,mode='real'):
    traces = []
    gamenums = range(1,len(e['price'])+1)
    colors={'price':'#8888BB','tritz':'#DD8888','elliott':'#88BB88'}
    for p in e:
        traces.append(
            go.Scatter(
                x = gamenums,
                y = e[p],
                name = p.title(),
                line = dict(color=colors[p], width = 4)
            )
        )

    # simple line chart
    #layout = dict(title='Elo', xaxis = dict(title = 'Game Number'), yaxis = dict(title = 'Elo rating'))

    layout = dict(
    title='Time series with range slider and selectors',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=30,
                    label='Last 30'),
                dict(count=100,
                    label='Last 100'),
                dict(count=len(e['price'])-471,
                    label='Bots only'),
                dict(step='all',
                    label='All')
                ])
            ),
            rangeslider=dict()
        )
    )

    fig = dict(data=traces, layout=layout)
    if mode == 'real':
        fn='elo'
    else:
        fn='Sim_elo'
    ploturl=py.plot(fig,filename=fn)
    return ploturl

def fooscharts(mode,results_file):
    elos={'price':[],'tritz':[],'elliott':[]}
    points={'price':[],'tritz':[],'elliott':[]}
    #point_totals=[]

    stats_file = open(results_file)
    reader = csv.reader(stats_file)
    for row in reader:
        elos['price'].append(float(row[5]))
        elos['tritz'].append(float(row[6]))
        elos['elliott'].append(float(row[7]))
        for score,player in zip(row[2:5],PLAYER_LIST):
            if score != '':
                points[player].append(int(score))

        #point_totals.append(int("0"+row[2])+int("0"+row[3])+int("0"+row[4]))
    stats_file.close()
    # ptc=point_total_chart(point_totals,mode)
    ptv=points_violin_chart(points,mode)
    ec=elo_chart(elos,mode)
    ev=elo_violin_chart(elos,mode)
    return {'Elo':ec,'Elo Violin':ev,'Point Violin':ptv}

def slack_post_charts(chart_urls):
    message = ''
    for chart in chart_urls:
        message += '*' + chart + ':* ' + chart_urls[chart] + '.embed' + '\n'
    payload = json.dumps({'text':message})
    requests.post(WEBHOOK_URL,data=payload)

if SIMULATION_MODE:
    numgames=2000000
    slack_say('Simulating ' + str(numgames) + ' games...')
    game_test(numgames,foos_json)
    # slack_post_charts(fooscharts('sim','/home/pricecomstock/slash-selfie/foosball/simresults.csv'))