import ast
from datetime import datetime

file_name = 'records.txt'

def read_grouped_records():
    records = read_records()
    grouped_records = {}
    for record in records:
        yday = datetime.fromtimestamp(records[0]['start_time']).timetuple().tm_yday
        if yday not in grouped_records.keys():
            grouped_records[yday] = record
        else:
            day_record = grouped_records[yday]
            day_record['duration'] += record['duration']
            day_record['total_balls'] += record['total_balls']
            day_record['total_hits'] += record['total_hits']
            if day_record['max_cont_hits'] < record['max_cont_hits']:
                day_record['max_cont_hits'] = record['max_cont_hits']
    print(grouped_records)
    return grouped_records 

def read_records():
    file = open(file_name, 'r')
    lines = file.readlines()
    records = list(map(string_to_dictionary, lines))
    return records
        
def append_to_file(data):
    file = open(file_name,'a')
    file.write(str(data) + '\n')

def string_to_dictionary(string_dictionary):
    return ast.literal_eval(string_dictionary)

if __name__ == '__main__':
    read_grouped_records()
