from flask import Flask

from League import League

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'