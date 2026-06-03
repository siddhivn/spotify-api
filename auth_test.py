import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

CLIENT_ID = "5c0626710e7c49a7a44fc495d21c46c8"
CLIENT_SECRET = "d4100fced29142249de2b7bd80a8d1a7"
REDIRECT_URI = "http://127.0.0.1:8080/callback"

scope = "user-read-currently-playing user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

print("Testing connection...")
while True:
    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None and current_track['is_playing']:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            track_id = current_track['item']['id']
            
            # Fetch audio features for energy score
            features = sp.audio_features(track_id)[0]
            energy = features['energy'] if features else 0.5
            
            print(f"Now Playing: {track_name} by {artist_name} [Energy: {energy}]")
        else:
            print("No music playing right now.")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3)
