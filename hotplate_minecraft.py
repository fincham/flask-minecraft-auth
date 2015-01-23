#!/usr/bin/env python

import os
import urllib2
import json

from flask import Flask, session, render_template, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form

from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['DEBUG'] = (os.environ['FLASK_DEBUG'] == 'True')
app.config['YGGDRASIL_CLIENT_TOKEN'] = os.environ['YGGDRASIL_CLIENT_TOKEN']

db = SQLAlchemy(app)

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

def _yggdrasil_request(payload, endpoint):
    req = urllib2.Request(
        url='https://authserver.mojang.com/%s' % endpoint,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )

    try:
        return json.loads(urllib2.urlopen(req).read())
    except ValueError:
        return None

def _yggdrasil_authenticate(username, password):
        payload = {
                "agent": {
                        "name": "Minecraft",
                        "version": 1,
                },
                "username": username,
                "password": password,
                "clientToken": app.config['YGGDRASIL_CLIENT_TOKEN'],
        }

        try:
            return _yggdrasil_request(payload, 'authenticate')
        except urllib2.HTTPError:
            return None

def _yggdrasil_invalidate(access_token):
        payload = {
                "accessToken": access_token,
                "clientToken": app.config['YGGDRASIL_CLIENT_TOKEN'],
        }

        try:
            return _yggdrasil_request(payload, 'invalidate') == None
        except urllib2.HTTPError:
            return False      

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        session['yggdrasil'] = _yggdrasil_authenticate(form.username.data, form.password.data)

        if session['yggdrasil']:
            flash('Logged in to Minecraft')
        else:
            flash('Could not log in to Minecraft')

        return redirect(url_for('index'))    

    return render_template(
        'login.html',
        form=form
    )

@app.route('/logout')
def logout():
    if 'yggdrasil' in session and _yggdrasil_invalidate(session['yggdrasil']['accessToken']):
        session.pop('yggdrasil', None)
        flash('Logged out') 

    return redirect(url_for('index'))    

if __name__ == '__main__' and app.config['DEBUG']:
    app.run()