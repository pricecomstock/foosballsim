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
with open(WORKING_DIR + 'current_standings.json') as standings_file:
    foos_json = json.load(standings_file)



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