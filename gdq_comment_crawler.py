import urllib.request
import re
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

def parse_donation(donation_id):
    try:
        req = urllib.request.Request(
            "https://gamesdonequick.com/tracker/donation/" + str(donation_id), 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.128 Safari/537.36 Shift/4.0.11'
            }
        )
    
        f = urllib.request.urlopen(req)
        soup = BeautifulSoup(f.read().decode('utf-8'), 'html.parser')
        if 'Object cannot be retrieved' in soup.title.string:
            raise Exception('Object cannot be retrieved')
        event = re.search('Donation Detail -- (.*)', soup.title.string).group(1)
        content = soup.body.find_all("div")[2]
        if '(Anonymous)' in str(content):
            username = '(Anonymous)'
            user_id = ""
        else:
            username = content.a.string
            user_id = re.search('/tracker/donor/(.*)/', content.a['href']).group(1)
        time_received = content.span.string
        donation = re.search('\\$(.*)', str(content.h2)).group(1)
        tables = content.find_all('table')
        num_tables = len(tables)
        
        if num_tables == 0:
            comment = ""
            bids = []
        elif num_tables == 1:
            if '/tracker/bid' in str(tables[0]):
                bids = get_bids(tables[0])
                comment = ""
            else:
                comment = tables[0].find_all('td')[0].text.strip()
                bids = []
        else:
            bids = get_bids(tables[1])
            comment = tables[0].find_all('td')[0].text.strip()
        bid_string = "~".join(f"bid_id={x['bid_id']}|run_id={x['run_id']}|amount={x['amount']}" for x in bids)
        
        return {
            'donation_id': donation_id,
            'event': event,
            'username': username,
            'time_received':time_received,
            'donation': donation,
            'comment': comment,
            'bids': bid_string,
            'user_id': user_id
        }
    except Exception as e:
        return {
            'donation_id': donation_id,
            'error': e
        }

def get_bids(tables):
    trs = tables.find_all('tr')
    bids = []
    for row in trs:
        tds = row.find_all('td')
        if len(tds) != 3:
            continue 

        run_id = ''
        if tds[0].a:
            run_id = re.search('/tracker/run/(.*)', tds[0].a['href']).group(1)
        bid_id = re.search('/tracker/bid/(.*)', tds[1].a['href']).group(1)
        amount = tds[2].string

        bids.append(
            {
                'run_id': run_id,
                'bid_id': bid_id,
                'amount': amount.strip()[1:]
            }
        )
    return bids
    
for donation_id in range(549709,665790): #665790
    donation = parse_donation(donation_id)
    if 'error' in donation:
        with open('errors.csv', 'a+', newline='', encoding='utf-8') as errorfile:
            efieldnames = ['donation_id', 'error']
            writer = csv.DictWriter(errorfile, fieldnames=efieldnames)
            writer.writerow(donation)
        print(donation['error'])
    else:
        with open('comments.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['donation_id', 'event', 'username', 'user_id', 'time_received', 'donation', 'comment', 'bids']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(donation)
        print('donation id ' + str(donation_id) + ' finished.')
    time.sleep(0.5)
    

