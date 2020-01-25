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
        event = re.search('Donation Detail -- (.*)', soup.title.string).group(1)
        content = soup.body.find_all("div")[2]
        if '(Anonymous)' in str(content):
            username = '(Anonymous)'
        else:
            username = content.a.string
        
        time_received = content.span.string
        donation = re.search('\\$(.*)', str(content.h2)).group(1)
        if content.table:
            comment = content.table.td.renderContents().strip()
            if '/tracker/run/' in str(comment):
                comment = ""
        else:
            comment = ""
        return {
            'donation_id': donation_id,
            'event': event,
            'username': username,
            'time_received':time_received,
            'donation': donation,
            'comment': comment
        }
    except Exception as e:
        return {
            'donation_id': donation_id,
            'error': e
        }


for donation_id in range(540221,665590): #665590
    donation = parse_donation(donation_id)
    if 'error' in donation:
        with open('errors.csv', 'a+', newline='', encoding='utf-8') as errorfile:
            efieldnames = ['donation_id', 'error']
            writer = csv.DictWriter(errorfile, fieldnames=efieldnames)
            writer.writerow(donation)
        print(donation['error'])
    else:
        with open('comments.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['donation_id', 'event', 'username', 'time_received', 'donation', 'comment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(donation)
        print('donation id ' + str(donation_id) + ' finished.')
    time.sleep(0.5)
