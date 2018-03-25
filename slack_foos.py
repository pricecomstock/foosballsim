from slack_config import WEBHOOK_URL
import requests

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