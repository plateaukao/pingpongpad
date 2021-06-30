from flask import Flask, request, abort, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/status", methods=['POST'])
def upload():
    if not request.json:
        abort(400)

    d = request.json.get("data", 0)
    print("receive data:{}".format(request.json))
    # do something

    # 回傳給前端
    socketio.emit('status_response', request.json)
    return jsonify(
        {"response": "ok"}
    )

@socketio.on('hit_status')
def update_status(request_json):
    socketio.emit('status_response', request_json)
    emit('hit_status_response', {'data': 'Server'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host="192.168.1.116")
    #socketio.run(app, debug=True)
    #socketio.run(app)
