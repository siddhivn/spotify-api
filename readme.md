### Phase 1: Operating System & Environment Setup

##### 1. Boot up and Update Your Pi
Turn on your Pi. Ensure it is connected to your Wi-Fi network via the desktop interface. Open the Terminal app on your desktop and update the system packages:
```
sudo apt update && sudo apt upgrade -y
```
##### 2. Create Your Project Directory
Create a dedicated space for your project files:
```
mkdir ~/spotify_desk_display
cd ~/spotify_desk_display
```
##### 3. Setup a Python Virtual Environment
Modern Raspberry Pi OS versions enforce isolated environments to keep your system stable.
```
python3 -m venv venv
source venv/bin/activate
```
##### Note: You will need to run source venv/bin/activate every time you open a new terminal to work on this project. Your terminal line will start with (venv) when active.

### Phase 2: Spotify API Setup & Core Connection

##### 1. Register Your App on Spotify
Go to the Spotify Developer Dashboard on your Pi's web browser or your computer, and log in.

- Click Create App.
- Name it Desk Companion Display.
- Set the Redirect URI to: http://127.0.0.1:8080/callback
- Save it, go to the app settings, and copy your Client ID and Client Secret.

##### 2. Install the Spotify Python Library
Inside your activated terminal ((venv)), run:
```
pip install spotipy
```

##### 3. Write Your First Test Script
Create a test file to fetch your live playback:
```
nano auth_test.py
```

Paste the following code (replace with your actual Spotify credentials):

```
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
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
```
Press Ctrl+O, then Enter to save, and Ctrl+X to exit.

#### note: cant use this code as spotify has restricted the audio features option and made it private so modified code is given below which only shows the artists name and the song playing.

```
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
```

(insert picture of output so far here)

##### 4. Run it and Authenticate
Run the script:
```
python auth_test.py
```
A browser window will pop up automatically on your Pi. Log in to Spotify, grant access, and once it redirects to a blank page or an error page showing localhost:8080, your terminal will come alive printing whatever song you play on your phone or computer.

### Phase 3: The Flask Server & Visual Dashboard
Now we want to build the local web application that will display the UI layout beautifully on your connected monitor.

1. Install Flask
Bash
pip install flask requests
2. Layout Your Folders
Flask expects a strict file structure to serve layout files:

Bash
mkdir templates static
3. Build the Frontend (templates/index.html)
Bash
nano templates/index.html
Paste this complete clean UI structure:

HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Mood Display</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: white;
            transition: background 1.5s ease;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        .container {
            text-align: center;
            background: rgba(0, 0, 0, 0.6);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            max-width: 400px;
            width: 100%;
        }
        #album-art {
            width: 250px;
            height: 250px;
            border-radius: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.6);
            margin-bottom: 20px;
        }
        h2 { margin: 10px 0 5px 0; font-size: 24px; }
        h3 { margin: 0 0 20px 0; font-size: 18px; color: #b3b3b3; }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            background: rgba(255,255,255,0.1);
        }
    </style>
</head>
<body>
    <div class="container" id="display-box">
        <img id="album-art" src="https://via.placeholder.com/250" alt="Album Art">
        <h2 id="track-name">Loading...</h2>
        <h3 id="artist-name">---</h3>
        <div class="status-badge" id="mood-badge">Mood: Calibrating</div>
        <p style="font-size:12px; color:#aaa;" id="presence-badge">Screen Active</p>
    </div>

    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                
                if (data.is_playing) {
                    document.getElementById('display-box').style.display = "block";
                    document.getElementById('track-name').innerText = data.song;
                    document.getElementById('artist-name').innerText = data.artist;
                    document.getElementById('album-art').src = data.album_art;
                    document.getElementById('mood-badge').innerText = "Mood: " + data.mood;
                    document.body.style.backgroundColor = data.color;
                } else {
                    document.getElementById('track-name').innerText = "Idling";
                    document.getElementById('artist-name').innerText = "Play a song on Spotify";
                    document.body.style.backgroundColor = "#121212";
                }
            } catch (err) {
                console.log("Error updating dashboard:", err);
            }
        }
        setInterval(updateDashboard, 2000); // Check every 2 seconds
    </script>
</body>
</html>
4. Create the Core Application Engine (app.py)
This merges the Spotify fetch engine and the dashboard app.

Bash
nano app.py
Paste this complete app architecture:

Python
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
Run python app.py, launch Chromium on your Pi, and navigate to http://localhost:5000. You will see a functional, beautiful dashboard reacting to your music changes in real-time.

Phase 4: Camera Integration (Presence / Smart Sleeping Mode)
Now we will hook up your hardware camera module to act as a physical presence detector. If you are absent for a prolonged period, your Pi can stop requesting data or hide the display.

1. Install OpenCV dependencies
Installing computer vision tools on linux systems takes a little extra lifting:

Bash
pip install opencv-python
2. Verify Your Camera works
Plug your USB Webcam or Pi Camera in. Let's make sure it's mounted:

Bash
ls /dev/video*
(You should see /dev/video0 listed).

3. Implement The Combined Presence Detection Script
We will add a secondary thread inside app.py that parses light background frames, detects changes (motion or face counting), and sets a global variable USER_PRESENT = True/False.

Open app.py again, and adjust it to look like this integrated design:

Python
import cv2
import threading
import time
from flask import Flask, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# --- CONFIG ---
CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8080/callback"

# Global System State
USER_PRESENT = True
last_seen_time = time.time()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI,
    scope="user-read-currently-playing user-read-playback-state"
))

def camera_presence_loop():
    global USER_PRESENT, last_seen_time
    # Initialize the default webcam interface
    cap = cv2.VideoCapture(0)
    
    # Load basic lightweight frontal face cascade model 
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        if len(faces) > 0:
            last_seen_time = time.time()
            USER_PRESENT = True
        else:
            # If nobody is detected for longer than 30 seconds
            if time.time() - last_seen_time > 30:
                USER_PRESENT = False
                
        time.sleep(1) # Inspect the camera frame once every second

# Fire up the camera engine in the background safely
cam_thread = threading.Thread(target=camera_presence_loop, daemon=True)
cam_thread.start()

def calculate_mood(valence, energy):
    if valence > 0.5 and energy > 0.5: return "Energetic", "#ff5722"
    elif valence > 0.5 and energy <= 0.5: return "Calm / Peaceful", "#4caf50"
    elif valence <= 0.5 and energy > 0.5: return "Intense / Dark", "#673ab7"
    else: return "Melancholic / Chill", "#2196f3"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def api_state():
    global USER_PRESENT
    
    # Smart Guard: If no one is around, hide the display completely
    if not USER_PRESENT:
        return jsonify({'is_playing': False, 'message': 'Display asleep - No listener detected.'})

    try:
        current_track = sp.current_user_playing_track()
        if current_track and current_track['is_playing']:
            item = current_track['item']
            features = sp.audio_features(item['id'])[0]
            v = features['valence'] if features else 0.5
            e = features['energy'] if features else 0.5
            mood_str, bg_color = calculate_mood(v, e)
            
            return jsonify({
                'is_playing': True,
                'song': item['name'],
                'artist': item['artists'][0]['name'],
                'album_art': item['album']['images'][0]['url'],
                'mood': mood_str,
                'color': bg_color
            })
    except Exception as err:
        print("Error fetching data:", err)
        
    return jsonify({'is_playing': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
5. Launch the Final Experience!
Run your updated app:

Bash
python app.py
Open http://localhost:5000 in Chromium, set the browser tab to Full Screen (F11), and place the display next to your desk!

When you sit down, your face updates USER_PRESENT, and your music metadata and colors fill the screen.

Step away from your desk for more than 30 seconds, and the screen will drop back to an idle dark theme to prevent display burn-in and save resources.
