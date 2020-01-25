import urllib.request
import re
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

def run_parser(url):
    try:
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.128 Safari/537.36 Shift/4.0.11'
            }
        )
    
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode('utf-8'), 'html.parser')
        content = soup.body.find_all("div")[2]
        run_table = content.table
        run_rows = run_table.find_all("tr")

        runs = []
        for row in run_rows:
            if not row.a:
                continue
            run_id = re.search('/tracker/run/(.*)', row.a['href']).group(1)
            spans = row.find_all("span")
            start_date = spans[0].string
            end_date = spans[1].string
            game = row.a.string
            
            tds = row.find_all("td")
            runners = str(tds[1].string).strip()
            description = str(tds[2].string).strip()

            runs.append({
                'runid': run_id,
                'start_date': start_date,
                'end_date': end_date,
                'game': game,
                'description': description,
                'runners': runners
            })

        return {
            'runs': runs
        }
    except Exception as e:
        return {
            'error': e
        }


runs = [
    #'https://gamesdonequick.com/tracker/runs/agdq2013',
     #'https://gamesdonequick.com/tracker/runs/agdq2014',
     #'https://gamesdonequick.com/tracker/runs/agdq2015',
    # 'https://gamesdonequick.com/tracker/runs/agdq2016',
    # 'https://gamesdonequick.com/tracker/runs/agdq2017',
     #'https://gamesdonequick.com/tracker/runs/agdq2018',
     #'https://gamesdonequick.com/tracker/runs/agdq2019',
     #'https://gamesdonequick.com/tracker/runs/agdq2020',
    # 'https://gamesdonequick.com/tracker/runs/sgdq2013',
     #'https://gamesdonequick.com/tracker/runs/sgdq2014',
     #'https://gamesdonequick.com/tracker/runs/sgdq2015',
    # 'https://gamesdonequick.com/tracker/runs/sgdq2016',
    # 'https://gamesdonequick.com/tracker/runs/sgdq2017',
    # 'https://gamesdonequick.com/tracker/runs/sgdq2018',
     #'https://gamesdonequick.com/tracker/runs/sgdq2019',
     #'https://gamesdonequick.com/tracker/runs/sgdq2012',
     #'https://gamesdonequick.com/tracker/runs/sgdq2011',
     #'https://gamesdonequick.com/tracker/runs/agdq2012',
     #'https://gamesdonequick.com/tracker/runs/hrdq',
]
for event in runs:
    events = run_parser(event)
    if 'error' in events:
        print(events['error'])
    else:
        with open('schedule.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['runid','start_date', 'end_date', 'runners', 'game', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for run in events['runs']:
                writer.writerow(run)
        