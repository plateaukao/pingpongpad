from flask import Flask, request, abort, render_template, jsonify
from flask_socketio import SocketIO, emit
import os, time
import subprocess
from track_records import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins=[], logger=True, engineio_logger=True)

cache = {
 'start_time' : 0,
 'duration' : 0, 
 'total_balls' : 0,
 'total_hits' : 0,
 'max_cont_hits' :0
}


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('hit_status')
def update_status(request_json):
    cache['total_balls'] = request_json['total_balls']
    cache['total_hits'] = request_json['total_hits']
    cache['max_cont_hits'] = request_json['max_cont_hits']
    duration = time.time() - cache['start_time']
    cache['duration'] = duration
    request_json['duration'] = '%02d:%02d:%02d' % (duration / 60 / 60, duration / 60 % 60, duration % 60)
    socketio.emit('status_response', request_json)
    #emit('hit_status_response', {'data': 'Server'})

@socketio.on('test_camera')
def test_camera():
    print("test camera")
    os.system('python3 detect_area_change.py -r -t')

@socketio.on('tracking')
def start_tracking():
    print("start tracking")
    cache['start_time'] = time.time()
    os.system('python3 detect_area_change.py -r -w')

@socketio.on('stop')
def stop_tracking():
    print("stop tracking")
    append_to_file(cache)
    subprocess.Popen("ps -A|grep detect_area_change|awk '{print $1}' | xargs kill -9", shell=True).communicate()
    

if __name__ == '__main__':
    socketio.run(app, debug=True, host="192.168.1.116")
    #socketio.run(app, debug=True)
    #socketio.run(app)
