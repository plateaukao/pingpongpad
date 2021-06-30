from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    f = open ('data.txt', 'r')
    return """
<html>
<head>
<meta http-equiv="refresh" content="1" >
</head>
<body>
""" + f.read() + "</body></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678)
