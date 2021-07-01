
def append_to_file(data):
    file = open('records.txt','a')
    file.write(str(data) + '\n')
    #file.write('%d:%d:%d:%d:%d:\n' % (start_time, duration, total_balls, total_hits, max_cont_hits))
