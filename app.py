#-*- encoding: UTF-8 -*-
import csv
import sqlite3
from flask import Flask, session, request, redirect, jsonify, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

# Our oauth
from oauth import Oauth

NCTU_APP_REDIRECT_URI = 'http://127.0.0.1:5000/auth'
NCTU_APP_CLIENT_ID = 'dFo3aTrp02yAzzHgaYNf90IUGe15ASgZfb6Wl2gb'
NCTU_APP_CLIENT_SECRET = 'dV2NgLReGwmKyfBIGajbVAZCAr7puGyudu1ZianSaIMV441Lo4udlPXloItyQTCGN3aHapPDV4OzNfb91Z1Hfm1HSEQkK9yKLt3vwtUc7JczIeDB7Rfo3nVqVgEuDbTY'

app = Flask(__name__)
app.secret_key = 'your super coll secrey key'
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

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/jwtlogin', methods=['POST'])
def jwtlogin():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    code = request.json.get('code', None)
    if not code:
        return jsonify({"msg": "Missing code parameter"}), 400

    if code != 'test':
        return jsonify({"msg": "Bad code"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=code)
    return jsonify(access_token=access_token), 200

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

if __name__ == "__main__":
    app.run(debug=1)

# FLASK_APP=app.py flask run
