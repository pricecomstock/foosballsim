import csv
import datetime

def starting_stats():
    d = {}
    d.setdefault('players',{})
    d.setdefault('overall',{})
    d['players'].setdefault('price',{'name':'price','games':0,'wins':0,'losses':0,'streak':{'type':'','length':0},'ps/g':-1.0,'pa/g':-1.0,'am+':-1.0,'am-':-1.0,'winpct':-1.0,'elo':1000})
    d['players'].setdefault('tritz',{'name':'tritz','games':0,'wins':0,'losses':0,'streak':{'type':'','length':0},'ps/g':-1.0,'pa/g':-1.0,'am+':-1.0,'am-':-1.0,'winpct':-1.0,'elo':1000})
    d['players'].setdefault('elliott',{'name':'elliott','games':0,'wins':0,'losses':0,'streak':{'type':'','length':0},'ps/g':-1.0,'pa/g':-1.0,'am+':-1.0,'am-':-1.0,'winpct':-1.0,'elo':1000})
    d['overall'].setdefault('king','')
    return d

def first_run_setup():
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