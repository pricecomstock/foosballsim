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