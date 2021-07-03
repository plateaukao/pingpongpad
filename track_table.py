from flask_table import Table, Col
from datetime import datetime
from track_records import *

# Declare your table
class DailyTable(Table):
    classes = ['table', 'table-striped']
    date = Col('Date')
    duration = Col('Duration')
    total_balls = Col('Total Balls')
    total_hits= Col('Total Hits')
    max_cont_hits = Col('Max Continuous Hits')

class DailyRecord(object):
    def __init__(self, object):
        self.date = object["date"].strftime("%m/%d")
        duration = object["duration"]
        self.duration = "%d:%02d" % (duration / 60, duration % 60)
        self.total_balls = object["total_balls"]
        self.total_hits = object["total_hits"]
        self.max_cont_hits = object["max_cont_hits"]

if __name__ == '__main__':
    records = read_grouped_records()
    mapped_records = map(DailyRecord, records.values())
    table = DailyTable(list(mapped_records))
    print(table.__html__())


# or just {{ table }} from within a Jinja template
