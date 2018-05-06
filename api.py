from flask import Flask

app = Flask(__name__)

from League import League

@app.route('/')
def hello():
    return 'Hello, World!'