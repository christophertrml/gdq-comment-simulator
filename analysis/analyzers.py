import datetime
from data_collector import get_speedruns_from_json
import json

runs = get_speedruns_from_json()
int_keys = [int(key) for key in runs]    
