import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['DEBUG'] = (os.environ['FLASK_DEBUG'] == 'True')

db = SQLAlchemy(app)

@app.route('/')
def hello():
    return "jubble"

if __name__ == '__main__' and app.config['DEBUG']:
    app.run()