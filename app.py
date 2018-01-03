#-*- encoding: UTF-8 -*-

from flask import Flask, session, request, redirect, jsonify

# Our oauth
from oauth import Oauth

NCTU_APP_REDIRECT_URI = 'http://127.0.0.1:5000/auth'
NCTU_APP_CLIENT_ID = 'dFo3aTrp02yAzzHgaYNf90IUGe15ASgZfb6Wl2gb'
NCTU_APP_CLIENT_SECRET = 'dV2NgLReGwmKyfBIGajbVAZCAr7puGyudu1ZianSaIMV441Lo4udlPXloItyQTCGN3aHapPDV4OzNfb91Z1Hfm1HSEQkK9yKLt3vwtUc7JczIeDB7Rfo3nVqVgEuDbTY'

app = Flask(__name__)
app.secret_key = 'your super coll secrey key'

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

@app.route('/auth')
def auth():
    # user code for getting token
    code = request.args.get('code')
    print(code)
    if code:
        #get user token
        if nctu.get_token(code):
            url = 'http://127.0.0.1:3000/?auth=' + code
            return redirect(url)
            # return jsonify(nctu.get_profile())

    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=1)


# FLASK_APP=app.py flask run
