# Python Gerneral
import sys
import uuid
import os
from dotenv import load_dotenv
import time
load_dotenv()

# Flask Modules
from flask import Flask, request, url_for, session, redirect, render_template
from flask_session import Session

# Spotify API Modules
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth 
from spotipy import oauth2

app = Flask(__name__, static_url_path="/static")
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

scope = 'user-library-read playlist-read-private user-read-recently-played'
home_url = 'spotify.evanshrestha.com'
home_url = ''

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URL')

cache_folder = './cache/'

TOKEN_INFO = 'token_info'

cache_folder = './cache/'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

def session_cache_path():
    return cache_folder + session.get('uuid')

def authorize_user():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    sp_oauth = oauth2.SpotifyOAuth(client_id = client_id,
                                   client_secret = client_secret,
                                   redirect_uri = redirect_uri,
                                   scope=scope,
                                   cache_path = session_cache_path())
    
    if request.args.get("code") is not None:
        code = sp_oauth.parse_response_code(request.url)
        token_info = sp_oauth.get_access_token(code)
        session["token"] = token_info['access_token']

    auth_url = sp_oauth.get_authorize_url()
    return auth_url

# index page
@app.route('/')
def get_home_page():
    return render_template('chat.html')

@app.route('/login')
def Login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('getTracks', _external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in!")
        return redirect(url_for('login', _external=False))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return str(sp.current_user_saved_tracks(limit = 50, offset = 0)['items'][0])

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(client_id = client_id,
                        client_secret = client_secret,
                        redirect_uri = url_for('redirect_page', _external=True), 
                        scope = scope)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)


    


