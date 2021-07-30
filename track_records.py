import ast
from datetime import datetime
import pytz

file_name = 'records.txt'

def read_grouped_records():
    records = read_records()
    grouped_records = {}
    for record in records:
        time_tuple = record['date'].timetuple()
        yday = time_tuple.tm_yday
        #print("month: " + str(time_tuple.tm_mon))
        #print("day: " + str(time_tuple.tm_mday))
        #print("hour: " + str(time_tuple.tm_hour))
        #print("duration: " + str(record['duration'] / 60))

        if yday not in grouped_records.keys():
            grouped_records[yday] = record
        else:
            day_record = grouped_records[yday]
            day_record['duration'] += record['duration']
            day_record['total_balls'] += record['total_balls']
            day_record['total_hits'] += record['total_hits']
            day_record['average_hits'] = int(record['total_hits'] / record['total_balls'])
            if day_record['max_cont_hits'] < record['max_cont_hits']:
                day_record['max_cont_hits'] = record['max_cont_hits']
    print(grouped_records)
    return grouped_records 

def read_records():
    file = open(file_name, 'r')
    lines = file.readlines()
    records = list(filter(filter_real_records, list(map(string_to_dictionary, lines))))
    for record in records:
        utc_dt = datetime.utcfromtimestamp(record['start_time'])
        #time_tuple = utc_dt.timetuple()
        aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        tz = pytz.timezone('Asia/Taipei')
        dt = aware_utc_dt.astimezone(tz)
        record['date'] = dt
    
    return records
        
def practice_data():
    records = read_records()

    day_color_red = 'rgba(255, 99, 132, 0.2)'
    day_color_orange = 'rgba(255, 159, 64, 0.2)'
    day_color = day_color_red

    data = {}
    data["labels"] = []
    data["datasets"] = []
    data["datasets"].append({ "type": "bar", "data": [], "backgroundColor": [], "label": "Practice Duration", "yAxisID": "duration" })
    data["datasets"].append({ "type": "line", "data": [], "label": "Total hits", "borderColor": 'rgb(75, 192, 192)',})
    data["datasets"].append({ "type": "line", "data": [], "label": "hits/ball", "borderColor": 'rgb(75, 75, 192)', "yAxisID": "averageBalls"})
    current_date_str = None
    for record in records:
        date_str = record["date"].strftime("%m/%d")
        time_str = record["date"].strftime("%H:%M")
        duration = int(record["duration"] / 60) + 1
        total_hits = record["total_hits"]
        average_hits = record["total_hits"] / record["total_balls"]
        if current_date_str == date_str:
            data["labels"].append(time_str)
        else:
            data["labels"].append(date_str + " " + time_str)
            current_date_str = date_str
            if day_color == day_color_red:
                day_color = day_color_orange
            else:
                day_color = day_color_red

        data["datasets"][0]["data"].append(duration)
        data["datasets"][0]["backgroundColor"].append(day_color)
        data["datasets"][1]["data"].append(total_hits)
        data["datasets"][2]["data"].append(average_hits)
    return data

def append_to_file(data):
    file = open(file_name,'a')
    file.write(str(data) + '\n')

def string_to_dictionary(string_dictionary):
    return ast.literal_eval(string_dictionary)

def filter_real_records(record):
    return record["total_hits"] > 30

if __name__ == '__main__':
    read_grouped_records()
