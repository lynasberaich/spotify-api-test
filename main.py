import os
from flask import Flask, request, redirect, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

#creates the actual web app
app = Flask(__name__)

#used to encrypt session information from users
app.secret_key = os.urandom(64)
#app.config['SECRET KEY'] = os.urandom(64)

#from spotify api website
client_id = 'fed06dbca8c34c02aab5d81cde14493e'
client_secret = '9f4b021e79334b9db31b49ebe5e1e744'
redirect_uri = 'https://spotify-api-test-un61.onrender.com/callback'
scope = 'playlist-read-private'

#manages the session
cache_handler = FlaskSessionCacheHandler(session)

#authetication manager
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,  
    cache_handler=cache_handler,
    show_dialog=True
)

#spotify client instance
sp = Spotify(auth_manager=sp_oauth)



#we now are going to write out first endpoint
# allows people to log in and see what parts of their data will be acessed
#creating homepage
@app.route('/')
def home():
    #check to see if they are logged in
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        #get them to log in
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))

#create endpoint where redirect happens
@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))

#create endpoint for actual task at hand: getting the playlists
@app.route('/get_playlists')
def get_playlists():
    #check to see if they are logged in
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        #get them to log in
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists(limit=8)
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    #playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    #in order to update flask route to html page
    return render_template('playlists.html', playlists=playlists_info)


#logout endpoint
@app.route('/logout')

def logout():
    session.clear()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
