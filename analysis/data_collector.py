from collections import defaultdict
from datetime import datetime
from lxml import html
import csv
import json
from re import sub

def get_speedruns():

    with open('..\\prizes.csv', newline='') as prize_file:
        next(prize_file)
        prizes = csv.reader(prize_file)
        run_id_to_prize_mapping = defaultdict(dict)
        for prize in prizes:
            prize_obj = {
                'prizeid': prize[0],
                'name': prize[1],
                'contributed_by': prize[2],
                'entry_threshold': prize[3],
                'category': prize[6],
                'image_link': prize[7]
            }
            if not prize[4].isdigit():
                continue
            start_run_id = int(prize[4])
            end_run_id = int(prize[5])
            for current_run_id in range(start_run_id, end_run_id + 1):
                if current_run_id not in run_id_to_prize_mapping:
                    continue
                if not 'prizes' in run_id_to_prize_mapping[current_run_id]:
                    run_id_to_prize_mapping[current_run_id]['prizes'] = []    
                run_id_to_prize_mapping[current_run_id]['prizes'].append(prize_obj)


    with open('..\\schedule.csv', newline='') as schedule_file:
        next(schedule_file)
        schedule = csv.reader(schedule_file)
        for run in schedule:
            run_id = int(run[0])
            
            run_id_to_prize_mapping[run_id]['run'] = {
                'start_date': datetime.strptime(run[1], "%m/%d/%Y %H:%M:%S %z"),
                'end_date': datetime.strptime(run[2], "%m/%d/%Y %H:%M:%S %z"),
                'runners': run[3],
                'game': run[4],
                'description': run[5]
            }
            run_id_to_prize_mapping[run_id]['bids'] = []
    bidObjs = {}
    with open('..\\bids.csv', newline='') as bid_file:
        next(bid_file)
        bids = csv.reader(bid_file)
        bidObjs = {}
        for bid in bids:
            bid_id = int(bid[0])
            parent_bid_string = bid[5]
            parent_bid_ids = []
            if parent_bid_string:
                parent_bid_ids = parent_bid_string.split('|')
            
            bidObjs[bid_id] = {
                'bid_id': bid_id,
                'name': bid[1],
                'description': bid[2],
                'amount': get_amount(bid[3]),
                'goal': get_amount(bid[4]),
                'parent_bid_ids': parent_bid_ids
            }


    with open('..\\comments.csv', newline='', encoding='utf-8') as comment_file:
        next(comment_file)
        comments = csv.reader(comment_file)
        
        start_time_index = {}
        end_time_index = {}
        for run_id, val in run_id_to_prize_mapping.items():
            start_time_index[val['run']['start_date']] = run_id
            end_time_index[val['run']['end_date']] = run_id

        i = 1
        closest_start_run_time = None
        closest_start_run_id = None
        closest_end_run_time = None
        closest_end_run_id = None
        for comment in comments: 
            commentObj = {
                'donation_id': int(comment[0]),
                'event': comment[1],
                'username': comment[2],
                'userid': comment[3],
                'time_received': datetime.strptime(comment[4], "%m/%d/%Y %H:%M:%S %z"), 
                'donation': get_amount(comment[5]),
                'comment': ''
            }

            attached_bids = []
            bid_str = comment[7] #bid_id=169|run_id=14|amount=400.00~bid_id=303|run_id=67|amount=100.00
            if bid_str:
                inner_bids = bid_str.split("~")
                for inner_bid in inner_bids:
                    bid_components = inner_bid.split("|")
                    run_id_parts = bid_components[1].split("=")
                    if run_id_parts.count == 2:
                        run_id = int(run_id_parts[1])
                    else:
                        run_id = 0

                    attached_bids.append({
                        'bid_id': int(bid_components[0].split("=")[1]),
                        'run_id': run_id,
                        'amount': get_amount(bid_components[2].split("=")[1])
                    })

            for attached_bid in attached_bids:
                if int(attached_bid['bid_id']) not in bidObjs:
                    continue
                if attached_bid['run_id'] == 0:
                    continue
                real_bid = bidObjs[int(attached_bid['bid_id'])]
                run_bids = run_id_to_prize_mapping[attached_bid['run_id']]['bids']
                if real_bid in run_bids:
                    continue
                run_bids.append(real_bid)
                
            commentObj['bids'] = attached_bids
            if comment[5] and not comment[6].isspace():
                try:
                    commentObj['comment'] = html.fromstring(comment[6]).text_content()
                except:
                    pass

            comment_time = commentObj['time_received']
            if not closest_start_run_time:
                closest_start_run_time = min(start_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_start_run_id = start_time_index[closest_start_run_time]
            if not closest_end_run_time:
                closest_end_run_time = min(end_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_end_run_id = end_time_index[closest_end_run_time]
            
            if closest_start_run_time <= comment_time <= closest_end_run_time:
                safe_append_comment_to_run(run_id_to_prize_mapping, closest_start_run_id, commentObj)
            else:
                
                closest_start_run_time = min(start_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_start_run_id = start_time_index[closest_start_run_time]
            
                closest_end_run_time = min(end_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_end_run_id = end_time_index[closest_end_run_time]

                closer_game_time = min([closest_start_run_time,closest_end_run_time], key=lambda d: abs(d - comment_time))
                if closer_game_time == closest_start_run_time:
                    safe_append_comment_to_run(run_id_to_prize_mapping, closest_start_run_id, commentObj)
                else:
                    safe_append_comment_to_run(run_id_to_prize_mapping, closest_end_run_id, commentObj)

            i = i + 1
            if i % 1000 == 0:
                print(i)
    return run_id_to_prize_mapping

def get_amount(maybe_curreny_str):
    if not maybe_curreny_str:
        return 0.0
    parsed_currency = sub(r'[^\d.]', '', maybe_curreny_str)
    if not parsed_currency:
        return 0.0
    return float(parsed_currency)

def get_speedruns_from_json():
    with open('speedruns.json', encoding='utf8') as json_file:
        return json.load(json_file)

def safe_append_comment_to_run(run_id_mapping, run_id_to_safe_append_to, comment_object):
    if not 'donations' in run_id_mapping[run_id_to_safe_append_to]:
        run_id_mapping[run_id_to_safe_append_to]['donations'] = []
    run_id_mapping[run_id_to_safe_append_to]['donations'].append(comment_object)

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()
