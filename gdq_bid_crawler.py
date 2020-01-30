import urllib.request
import re
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

def run_parser(url):
   
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
    bid_table = content.table
    bid_rows = bid_table.find_all("tr")

    bids = []
    for row in bid_rows:
        if not row.a:
            continue
            
        tds = row.find_all("td")
        
        if tds[0].table:
            parent_bid_id = re.search('bidOptionData-([0-9]*)', row.get('id')).group(1)
            add_bid_options_to_bids(tds[0].table.tbody, [parent_bid_id], bids)
            continue

        bid_id = re.search('/tracker/bid/(.*)', tds[0].a['href']).group(1)
        if has_bid_has_already_been_recorded(bids, bid_id):
            continue
        bid_name = tds[0].a.string.strip()
        bid_description = tds[3].string.strip()
        amount = tds[4].string.strip()[1:]
        goal = tds[5].string.strip()
        parent_bid_ids = [""]
        if '$' in goal:
            goal = goal[1:]

        bids.append({
            'bidid': bid_id,
            'name': bid_name,
            'description': bid_description,
            'amount': amount,
            'goal': goal,
            'parent_bid_ids': parent_bid_ids
        })

    return {
        'bids': bids
    }

def has_bid_has_already_been_recorded(bids, bid_id_to_check):
    for check in bids:
        if check['bidid'] == bid_id_to_check:
            return True
    return False

def add_bid_options_to_bids(table, parent_bid_ids, bids):
    options_trs = table.find_all('tr')
    bid_options = []
    for option in options_trs:
        if option.get('id') and 'bidOptionData' in option.get('id'):
            new_parent_bid_id = re.search('bidOptionData-([0-9]*)', option.get('id')).group(1)
            bid_options = bid_options + add_bid_options_to_bids(option.td.table.tbody, parent_bid_ids + [new_parent_bid_id] , bids)
            continue
        option_tds = option.find_all('td')
        if len(option_tds) == 0:
            continue
        if option_tds[0].a:
            
            option_bid_id = re.search('/tracker/bid/(.*)', option_tds[0].a['href']).group(1)

            if has_bid_has_already_been_recorded(bids, option_bid_id):
                continue
            option_bid_name = option_tds[0].a.string.strip()
            option_description = option_tds[3].string.strip()
            option_amount_donated = option_tds[4].string.strip()[1:]
            bids.append({
                    'bidid': option_bid_id,
                    'name': option_bid_name,
                    'description': option_description,
                    'amount': option_amount_donated,
                    'goal': "N/A",
                    'parent_bid_ids': '|'.join(parent_bid_ids)
            })
    
    return bids

runs = [
    'https://gamesdonequick.com/tracker/bids/agdq2013',
     #'https://gamesdonequick.com/tracker/bids/agdq2014',
     'https://gamesdonequick.com/tracker/bids/agdq2015',
    'https://gamesdonequick.com/tracker/bids/agdq2016',
    'https://gamesdonequick.com/tracker/bids/agdq2017',
     'https://gamesdonequick.com/tracker/bids/agdq2018',
     'https://gamesdonequick.com/tracker/bids/agdq2019',
     'https://gamesdonequick.com/tracker/bids/agdq2020',
    'https://gamesdonequick.com/tracker/bids/sgdq2013',
     'https://gamesdonequick.com/tracker/bids/sgdq2014',
     'https://gamesdonequick.com/tracker/bids/sgdq2015',
    'https://gamesdonequick.com/tracker/bids/sgdq2016',
    'https://gamesdonequick.com/tracker/bids/sgdq2017',
    'https://gamesdonequick.com/tracker/bids/sgdq2018',
     'https://gamesdonequick.com/tracker/bids/sgdq2019',
     'https://gamesdonequick.com/tracker/bids/sgdq2012',
     'https://gamesdonequick.com/tracker/bids/sgdq2011',
     'https://gamesdonequick.com/tracker/bids/agdq2012',
     'https://gamesdonequick.com/tracker/bids/hrdq',
]
for event in runs:
    events = run_parser(event)
    with open('bids.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['bidid','name', 'description', 'amount', 'goal', 'parent_bid_ids']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for run in events['bids']:
            writer.writerow(run)
    print('event done ' + event)
    time.sleep(5)
        