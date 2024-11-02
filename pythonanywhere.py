import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import csv
from datetime import datetime
import logging
LOG_FILENAME = 'log.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth("c0a7d2118fed424fbb992ca2803a4420",
#                                               "fe0919cefb7a4a23a34f5c248fec8ede",
#                                               "http://127.0.0.1:9090/callback",
#                                               "user-library-read user-read-playback-state user-read-recently-played"))
# access_token = "BQBxaGBmNrF5ZPUK5rvtSeGIugIfaSvMysBJXKj6kSVTqxJZtZkSTJohsRnQhcOeFAxWjtPuVxeHq0qS4x-6U2zm5d4z_U8iw7VdlRoTLWjlwfnrNZHM3Z_YLjDM80mIqniaLdOiQ8UZC1hGKVzpBCTAoMz6v3YJCqx59ehzUXzrHBs_OBXTvHq1L45eEg6-Hsk-TnXg9W0oHxzy2pPrl1Yf0eoBF0hg9O0"
# sp = spotipy.Spotify(auth=access_token)

# Manually provided access token and refresh token (replace with your tokens)
ACCESS_TOKEN = "BQBxaGBmNrF5ZPUK5rvtSeGIugIfaSvMysBJXKj6kSVTqxJZtZkSTJohsRnQhcOeFAxWjtPuVxeHq0qS4x-6U2zm5d4z_U8iw7VdlRoTLWjlwfnrNZHM3Z_YLjDM80mIqniaLdOiQ8UZC1hGKVzpBCTAoMz6v3YJCqx59ehzUXzrHBs_OBXTvHq1L45eEg6-Hsk-TnXg9W0oHxzy2pPrl1Yf0eoBF0hg9O0"
REFRESH_TOKEN = "AQDivZuIJni0yeEVzFqDUH4E5nDAEdY12KyrcvWf8IBzbZ9933XGf2-c1eSh0-4mS_yzDk8iZRKsGYRHvU2rW8l2dxpKpFStFE7FMGvIcQfBi-7Uf19kiI4e9oAKQr9dlzU"

# Spotify client credentials (replace with your Spotify app credentials)
CLIENT_ID = "c0a7d2118fed424fbb992ca2803a4420"
CLIENT_SECRET = "fe0919cefb7a4a23a34f5c248fec8ede"
REDIRECT_URI = "http://127.0.0.1:9090/callback"
SCOPE = "user-library-read user-read-playback-state user-read-recently-played"

# Initialize SpotifyOAuth for refreshing the token
auth_manager = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=SCOPE,
                            cache_path=".cache")

# Set up the Spotify client using the initial access token
sp = spotipy.Spotify(auth=ACCESS_TOKEN)

# Function to refresh the access token using the refresh token if needed
def refresh_token_if_needed():
    global sp
    try:
        # Try making an API call, if it fails due to token expiration, refresh it
        sp.current_playback()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:  # Token expired
            print("Access token expired, refreshing...")
            new_token_info = auth_manager.refresh_access_token(REFRESH_TOKEN)
            new_access_token = new_token_info['access_token']
            print(f"New access token: {new_access_token}")
            sp = spotipy.Spotify(auth=new_access_token)
            logging.exception('Got exception due to token expiring, refreshed token')

# Function to get the current song information
def get_current_song():
    refresh_token_if_needed()  # Refresh token if it has expired
    try:
        playback = sp.current_playback()
        if playback and playback['is_playing']:
            current_track = playback['item']
            song_name = current_track['name']
            artist_name = current_track['artists'][0]['name']
            progress_ms = playback['progress_ms']  # Current progress in milliseconds
            duration_ms = current_track['duration_ms']  # Total song duration in milliseconds
            return song_name, artist_name, progress_ms, duration_ms
        else:
            return None, None, None, None
    except spotipy.SpotifyException as e:
        print(f"Error retrieving current song: {e}")
        logging.exception('Got exception in trying to retrieve the song')
        return None, None, None, None

# Function to log the song to a CSV file
def log_song_to_csv(song_name, artist_name, duration_ms):
    timestamp = datetime.now()  # Get the current timestamp
    date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format it to readable date and time

    # Append the song info to a CSV file
    try:
        with open('listening_history.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date_str, song_name, artist_name, duration_ms])
            print(f"Logged: {song_name} by {artist_name} at {date_str} with duration {duration_ms}")
    except Exception as e:
        print(f'Error logging to CSV: {e}')
        logging.exception('Got exception when trying to append the song to the CSV file')

# Function to monitor playback and detect song repeats/loops
def monitor_playback():
    last_song = None
    last_artist = None
    last_progress = 0

    while True:
        # Get the current song, artist, progress, and duration
        song, artist, progress_ms, duration_ms = get_current_song()

        if song and duration_ms:  # Ensure the song and duration are available

            # Detect if a new song is playing
            if song != last_song:
                print(f"Currently playing: {song} by {artist}")
                if last_song != None:
                    log_song_to_csv(last_song, last_artist, last_progress)
                last_artist = artist
                last_song = song
                last_progress = progress_ms

            # Detect if the same song is being repeated (either naturally looped or restarted)
            else:
                # Check if the song is near its end and has restarted
                if progress_ms < last_progress and last_progress > (0.70 * duration_ms):  # If the song was close to the end (50%) and restarted
                    print(f"{song} by {artist} is being repeated")
                    print(duration_ms)
                    log_song_to_csv(song, artist, last_progress)

            # Update the progress for the current song
            last_progress = progress_ms

        else:
            # Handle the case where there is no song playing or an error occurred
            print("No song is currently playing or an error occurred.")

        # Wait for a few seconds before checking again
        time.sleep(5)


# Start monitoring the user's playback
if __name__ == "__main__":
    try:
        monitor_playback()
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
        logging.exception('User ended run')
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")
        logging.exception('Error occured that has not been accounted for!')
