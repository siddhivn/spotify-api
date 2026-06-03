from flask import Flask, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8080/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
    scope="user-read-currently-playing user-read-playback-state"
))

def calculate_mood(valence, energy):
    # Mood Mapping Logic Layer
    if valence > 0.5 and energy > 0.5:
        return "Energetic / Happy", "#ff5722" # Warm Orange/Vibrant Red
    elif valence > 0.5 and energy <= 0.5:
        return "Calm / Peaceful", "#4caf50"  # Relaxing Green
    elif valence <= 0.5 and energy > 0.5:
        return "Intense / Dark", "#673ab7"   # Deep Purple
    else:
        return "Melancholic / Chill", "#2196f3" # Blue

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def api_state():
    try:
        current_track = sp.current_user_playing_track()
        if current_track and current_track['is_playing']:
            item = current_track['item']
            track_id = item['id']
            
            # Fetch dynamic parameters
            features = sp.audio_features(track_id)[0]
            valence = features['valence'] if features else 0.5
            energy = features['energy'] if features else 0.5
            
            mood_string, background_color = calculate_mood(valence, energy)
            
            return jsonify({
                'is_playing': True,
                'song': item['name'],
                'artist': item['artists'][0]['name'],
                'album_art': item['album']['images'][0]['url'],
                'mood': mood_string,
                'color': background_color
            })
    except Exception as e:
        print("API Error:", e)
        
    return jsonify({'is_playing': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
