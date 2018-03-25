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