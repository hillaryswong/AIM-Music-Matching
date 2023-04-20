# Python Gerneral
import uuid
import os

# Spotify API Modules
import spotipy
from spotipy import oauth2

# Dot Env
from dotenv import load_dotenv
load_dotenv()

# Flask Modules
from flask import Flask, request, url_for, session, redirect, render_template
from flask_session import Session


app = Flask(__name__, template_folder="templates", static_url_path="/static")
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)

app.secret_key = "K4%jge$i9!ov6CrW8^y$28%$@ktzNLFTy"
# app.config['SESSION_COOKIE_NAME'] = "Lovify My Cookies"

Session(app)

home_url = '' # ill get to this

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
scope = os.getenv('SCOPE')
redirect_uri = "http://localhost:5000/redirect-user"



cache_folder = './cache/'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)


def session_cache_path():
    return cache_folder + session.get('uuid')

def authorize_user():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    sp_oauth = oauth2.SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, 
        scope=scope, cache_path = session_cache_path())
    
    if request.args.get("code") is not None:
        code = sp_oauth.parse_response_code(request.url)
        token_info = sp_oauth.get_access_token(code)
        session["token"] = token_info['access_token']

    auth_url = sp_oauth.get_authorize_url()
    return auth_url



# Index page
@app.route('/')
def home_page():
    if 'token' in session:
        sp = spotipy.Spotify(auth=session["token"])
        return login_redirect(sp)
    else:
        return render_template('index.html')


# About page
@app.route('/what-about-us')
def about_page():
    return render_template('about.html')


# Compatibility page
@app.route('/find-compatibility', methods=["GET", "POST"])
def compatibility_page():
    return render_template('compatibility.html')

# Login
@app.route('/login')
def login_redirect():
    if "token" in session:
        return redirect(url_for('logged_in_user'))
    auth = authorize_user()
    return redirect(auth)

# Logged in
@app.route('/redirect-user')
def logged_in_user(sp=None):
    if "token" in session:
        sp = spotipy.Spotify(auth=session["token"])
    else:
        auth = authorize_user()
        return redirect(auth)

    try:
        user = sp.current_user()
    except spotipy.client.SpotifyException:
        return redirect(url_for('login_redirect'))

    user_name = user['display_name']
    user_photo = user['images'][0]['url']
    user_uri = user['uri']

    return render_template("user_index.html", user_name=user_name, user_photo=user_photo, user_uri=user_uri)


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port='5000')