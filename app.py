from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Heipparallaa!"

@app.route('/counter')
def test():
    cont = ''
    for i in range(100):
        cont += str(i)+' '
    return cont