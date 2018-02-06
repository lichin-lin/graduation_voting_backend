#-*- encoding: UTF-8 -*-
import csv
import sqlite3
import requests
from datetime import datetime
from flask import Flask, session, request, redirect, jsonify, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_optional,
    get_jwt_identity
)
from flask_cors import (
    CORS,
    cross_origin
)

# Our oauth
from oauth import Oauth
OAUTH_URL = 'https://id.nctu.edu.tw'
NCTU_APP_REDIRECT_URI = 'https://107songs.nctu.me/'
NCTU_APP_CLIENT_ID = 'dFo3aTrp02yAzzHgaYNf90IUGe15ASgZfb6Wl2gb'
NCTU_APP_CLIENT_SECRET = 'dV2NgLReGwmKyfBIGajbVAZCAr7puGyudu1ZianSaIMV441Lo4udlPXloItyQTCGN3aHapPDV4OzNfb91Z1Hfm1HSEQkK9yKLt3vwtUc7JczIeDB7Rfo3nVqVgEuDbTY'

app = Flask(__name__, static_url_path='')
app.secret_key = 'your super coll secrey key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)
SQLITE_DB_PATH = 'songs.db'
SQLITE_DB_SCHEMA = 'create_db.sql'
MEMBER_CSV_PATH = 'songs.csv'

# make a oauth init
nctu = Oauth(
    redirect_uri=NCTU_APP_REDIRECT_URI,
    client_id=NCTU_APP_CLIENT_ID,
    client_secret=NCTU_APP_CLIENT_SECRET
)

@app.route("/backend")
def home():
    # check if login
    if session.get('logged_in'):
        # get user profile
        return jsonify(nctu.get_profile())
    writeLog('not login user try to login')
    return redirect('/login')

@app.route('/login')
@cross_origin()
def login():
    # redirect to nctu auth dialog
    return nctu.authorize()

@app.route('/vote', methods=['GET'])
@cross_origin()
@jwt_required
def vote():
    # 先測 token, 再去問 oauth
    current_user = get_jwt_identity()
    # 再測一下 id
    print('current_user: ', current_user)
    songID = request.args.get('songid')
    memberID = current_user['username']

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
        # writeLog('create new voting record', voting_result)
        print('create new voting record', voting_result)
        return jsonify('vote!'), 200
    else:
        # writeLog('you already vote: song', voting_result)
        print('you already vote: song', voting_result)
        return jsonify('already vote!'), 200
    return redirect('/')

@app.route('/auth')
@cross_origin()
def auth():
    # user code for getting token
    code = request.args.get('code')
    print(code)
    if code:
        #get user token
        print('decide')
        if nctu.get_token(code):
            # writeLog('auth success' + nctu.get_profile().get('Age'))
            print(nctu.get_profile(), 'user: ', nctu.get_profile().get('Age'))
            profile = nctu.get_profile()
            access_token = create_access_token(identity=profile)
            # url = 'http://127.0.0.1:3000/?accesstoken=' + access_token
            # return redirect(url)
            return jsonify(access_token=access_token, profile=profile), 200

    return redirect('https://107songs.nctu.me/login')

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

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

def writeLog(text):
    printText = '[' + str(datetime.now()) + '] ' + text + '\n'
    print(printText)
    f = open('log.txt', 'a')
    f.write(printText)
    f.close()

if __name__ == "__main__":
    app.run(debug=1, host='0.0.0.0')

# FLASK_APP=app.py flask run
