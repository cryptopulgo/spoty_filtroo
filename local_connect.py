import requests
from flask import Flask, request, redirect, jsonify, session, url_for
import os
import urllib.parse
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'una_clave_secreta'

# Configuración
CLIENT_ID = '6f73f847c3834434b491df088254e117'
CLIENT_SECRET = 'c0906342ffa041f8991f906cdd112e86'
# CLIENT_ID = '297165d4505b4c06b5be382a276737a4' # potota
# CLIENT_SECRET = 'ff35fa2a08da4286afbea5ffb4aeea4c' # potota
REDIRECT_URI = 'http://localhost:8888/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route('/')
def index():
    return "Welcome to my spotify app <a href='/login'>Login with Spotify</a>"


@app.route('/login')
def login():
    scope = (
            "user-read-private "
            "user-read-email "
            "playlist-read-private "
            "playlist-read-collaborative "
            "user-library-read "
            "user-top-read "
            "user-read-playback-state "
            "user-read-currently-playing "
            "user-read-recently-played "
            "user-follow-read "
        )
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})

    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        print('-----------')
        print(token_info)
        print('-----------')

        return redirect('/playlists')


@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}",
    }
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    playlists = response.json()

    return jsonify(playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/get_playlists')


if __name__ == '__main__':
    app.run(debug=True, port=8888)