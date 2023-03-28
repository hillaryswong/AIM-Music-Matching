#PURPOSE OF THE NEO-POOLER SYSTEM IS TO CREATE A NEW POOL OF SONGS SIMILAR
#TO SONGS IN A USER'S LIKED AND MATCHIFY LIKED PLAYLISTS

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ["SPOTIPY_CLIENT_ID"],
                                               client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
                                               redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
                                               scope="playlist-modify-private,user-library-read"))

#GETTING USER SPECIFIC DATA:
def get_user_id():
    user = sp.current_user()
    return user['id']

#   CONT'D
def get_playlist_id(playlist_name):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']
    return None

#   CONT'D
def get_tracks_from_playlists(playlist_ids):
    track_ids = set()
    for playlist_id in playlist_ids:
        tracks = sp.playlist_tracks(playlist_id)
        for item in tracks['items']:
            track = item['track']
            track_ids.add(track['id'])
    return list(track_ids)

#TODO: REPLACE SPOTIFY API FUNCTION '.recommendations()' WITH OUR OWN IN-HOUSE AI SYSTEM
#Alternatively, it may be wise to fall back on Spotify's '.recommendations()' function
#if a songs lacks too much vital metadata.
def recommend_songs(seed_tracks, limit=20):
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit)
    return [track['id'] for track in recommendations['tracks']]

#creates the playlist of new, similar songs. might have to mess around with scope/permissions to
#get this to work properly
def create_playlist_with_recommendations(user_id, recommended_tracks):
    new_playlist = sp.user_playlist_create(user_id, "Recommended Songs", public=False)
    sp.playlist_add_items(new_playlist['id'], recommended_tracks)

#TEST MAIN
def main():
    user_id = get_user_id()
    liked_songs_id = get_playlist_id("Liked Songs")
    liked_songs_matchify_id = get_playlist_id("Liked Songs - Matchify")

    playlist_ids = [liked_songs_id]
    if liked_songs_matchify_id:
        playlist_ids.append(liked_songs_matchify_id)

    track_ids = get_tracks_from_playlists(playlist_ids)
    recommended_tracks = recommend_songs(track_ids)
    create_playlist_with_recommendations(user_id, recommended_tracks)

if __name__ == "__main__":
    main()
