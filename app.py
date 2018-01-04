#-*- encoding: UTF-8 -*-
import csv
import sqlite3
from flask import Flask, session, request, redirect, jsonify, g
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

# Our oauth
from oauth import Oauth

NCTU_APP_REDIRECT_URI = 'http://127.0.0.1:5000/auth'
NCTU_APP_CLIENT_ID = 'dFo3aTrp02yAzzHgaYNf90IUGe15ASgZfb6Wl2gb'
NCTU_APP_CLIENT_SECRET = 'dV2NgLReGwmKyfBIGajbVAZCAr7puGyudu1ZianSaIMV441Lo4udlPXloItyQTCGN3aHapPDV4OzNfb91Z1Hfm1HSEQkK9yKLt3vwtUc7JczIeDB7Rfo3nVqVgEuDbTY'

# JWT
class User(object):
    def __init__(self, id, usercode):
        self.id = id
        self.usercode = usercode

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    User(1, '7gTeaXHzIjjRi7UPHqygnBnORpr0hQ'),
    User(2, '123')
]

usercode_table = {u.usercode: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(usercode):
    user = usercode_table.get(usercode, None)
    if user and safe_str_cmp(user.usercode.encode('utf-8'), usercode.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)
# JWT
app = Flask(__name__)
app.secret_key = 'your super coll secrey key'
jwt = JWT(app, authenticate, identity)
SQLITE_DB_PATH = 'songs.db'
SQLITE_DB_SCHEMA = 'create_db.sql'
MEMBER_CSV_PATH = 'songs.csv'

# make a oauth init
nctu = Oauth(
    redirect_uri=NCTU_APP_REDIRECT_URI,
    client_id=NCTU_APP_CLIENT_ID,
    client_secret=NCTU_APP_CLIENT_SECRET
)

@app.route("/")
def home():
    # check if login
    if session.get('logged_in'):
        # get user profile
        return jsonify(nctu.get_profile())

    return redirect('/login')

@app.route('/login')
def login():
    # redirect to nctu auth dialog
    return nctu.authorize()

@app.route('/vote')
def vote():
    # 先測 token
    # ...
    # 再測一下 id
    songID = request.args.get('songid')
    memberID = request.args.get('memberid')

    db = get_db()

    voting_result = db.execute(
        'SELECT memberid, songid FROM voting_record WHERE memberid = ?',
        (memberID, )
    ).fetchone()

    if voting_result is None:
        vote = db.execute(
            'INSERT INTO  voting_record (memberid, songid) VALUES (?, ?)',
            (memberID, songID)
        )
        print('create new voting record', voting_result)
    else:
        print('you already vote: song', voting_result)

    # return redirect('/')
    return redirect('/')

@app.route('/auth')
def auth():
    # user code for getting token
    code = request.args.get('code')
    print(code)
    if code:
        #get user token
        if nctu.get_token(code):
            url = 'http://127.0.0.1:3000/?code=' + code
            return redirect(url)

    return redirect('/login')

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

# SQLite3-related operations
# See SQLite3 usage pattern from Flask official doc
# http://flask.pocoo.org/docs/0.10/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH, isolation_level=None)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=1)

# FLASK_APP=app.py flask run
