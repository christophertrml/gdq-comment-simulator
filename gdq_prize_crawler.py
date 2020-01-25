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

        prizes = []
        for row in run_rows:
            if not row.a:
                continue
            
            tds = row.find_all("td")
            
            run_td = tds[0]
            contributed_by_td = tds[1]
            entry_threshold_td = tds[2]
            games_td = tds[3]
            category_td = tds[4]
            image_td = tds[5]

            prize_id = re.search('/tracker/prize/(.*)', run_td.a['href']).group(1)
            name = run_td.a.string
            contributed_by = contributed_by_td.string
            entry_threshold = entry_threshold_td.string
            if not games_td.a:
                start_game_id = 'N/A'
                end_game_id = 'N/A'
            else:
                if games_td.i:
                    game_links = games_td.find_all('a')
                    start_game_id = re.search('/tracker/run/(.*)', game_links[0]['href']).group(1)
                    end_game_id = re.search('/tracker/run/(.*)', game_links[1]['href']).group(1)
                else:
                    game_id = re.search('/tracker/run/(.*)', games_td.a['href']).group(1)
                    start_game_id = game_id
                    end_game_id = game_id

            if image_td.a:
                image_link = image_td.a['href']
            else:
                image_link = 'None'

            category = category_td.string
            
            prizes.append({
                'prizeid': prize_id,
                'name': name.strip(),
                'contributed_by': contributed_by.strip(),
                'entry_threshold': entry_threshold.strip().replace('\n', ' '),
                'start_game_id': start_game_id,
                'image_link': image_link,
                'category': category.strip(),
                'end_game_id': end_game_id
            })
            

        return {
            'prizes': prizes
        }
    except Exception as e:
        return {
            'error': e
        }


prizes = [
    #'https://gamesdonequick.com/tracker/prizes/agdq2013',
     #'https://gamesdonequick.com/tracker/prizes/agdq2014',
     #'https://gamesdonequick.com/tracker/prizes/agdq2015',
     #'https://gamesdonequick.com/tracker/prizes/agdq2016',
     #'https://gamesdonequick.com/tracker/prizes/agdq2017',
     #'https://gamesdonequick.com/tracker/prizes/agdq2018',
     #'https://gamesdonequick.com/tracker/prizes/agdq2019',
     #'https://gamesdonequick.com/tracker/prizes/agdq2020',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2013',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2014',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2015',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2016',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2017',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2018',
     #'https://gamesdonequick.com/tracker/prizes/sgdq2019',
     #'https://gamesdonequick.com/tracker/prizes/hrdq',
]
for event in prizes:
    events = run_parser(event)
    if 'error' in events:
        print(events['error'])
    else:
        with open('prizes.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['prizeid', 'name', 'contributed_by', 'entry_threshold', 'start_game_id', 'end_game_id', 'category', 'image_link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for run in events['prizes']:
                writer.writerow(run)
                #print(run)
                
        