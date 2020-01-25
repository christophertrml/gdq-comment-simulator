from collections import defaultdict
from datetime import datetime
import csv

def get_donations():

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

    current_run_index_pointer = 0

    with open('..\\comments_bak.csv', newline='', encoding='utf-8') as comment_file:
        next(comment_file)
        comments = csv.reader(comment_file)
        comment_results = []
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
                'time_received': datetime.strptime(comment[3], "%m/%d/%Y %H:%M:%S %z"), 
                'donation': comment[4],
                'comment': comment[5]
            }
            comment_time = commentObj['time_received']
            if not closest_start_run_time:
                closest_start_run_time = min(start_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_start_run_id = start_time_index[closest_start_run_time]
            if not closest_end_run_time:
                closest_end_run_time = min(end_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_end_run_id = end_time_index[closest_end_run_time]
            
            if closest_start_run_time <= comment_time <= closest_end_run_time:
                commentObj['speedrun'] = run_id_to_prize_mapping[closest_start_run_id]
            else:
                
                closest_start_run_time = min(start_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_start_run_id = start_time_index[closest_start_run_time]
            
                closest_end_run_time = min(end_time_index.keys(), key=lambda d: abs(d - comment_time))
                closest_end_run_id = end_time_index[closest_end_run_time]

                closer_game_time = min([closest_start_run_time,closest_end_run_time], key=lambda d: abs(d - comment_time))
                if closer_game_time == closest_start_run_time:
                    commentObj['speedrun'] = run_id_to_prize_mapping[closest_start_run_id]
                else:
                    commentObj['speedrun'] = run_id_to_prize_mapping[closest_end_run_id]

            comment_results.append(commentObj)
            i = i + 1
            if i % 1000 == 0:
                print(i)

            if i > 15000:
                break
        return comment_results