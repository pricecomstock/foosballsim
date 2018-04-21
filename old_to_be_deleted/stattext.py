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