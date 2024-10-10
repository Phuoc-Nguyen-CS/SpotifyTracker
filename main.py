import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import csv
from datetime import datetime
import env

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(env.SPOTIPY_CLIENT_ID,
                                               env.SPOTIPY_CLIENT_SECRET,
                                               env.SPOTIPY_REDIRECT_URI,
                                               scope=env.scope))

# Function to get the current song information
def get_current_song():
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

# Function to monitor playback and detect song repeats/loops
def monitor_playback():
    last_song = None
    last_progress = None
    repeat_count = 0  # Track how many times the song has been repeated

    while True:
        # Get the current song, artist, progress, and duration
        song_name, artist_name, progress_ms, duration_ms = get_current_song()

        if song_name and duration_ms:  # Ensure the song and duration are available

            # Detect if a new song is playing
            if song_name != last_song:
                print(f"Currently playing: {song_name} by {artist_name}")
                log_song_to_csv(song_name, artist_name, duration_ms)
                last_song = song_name
                last_progress = progress_ms
                repeat_count = 0  # Reset repeat count for new song

            # Detect if the same song is being repeated (either naturally looped or restarted)
            else:
                # Check if the song is near its end and has restarted
                if progress_ms < last_progress and last_progress > (0.95 * duration_ms):  # If the song was close to the end (95%) and restarted
                    repeat_count += 1
                    print(f"{song_name} by {artist_name} is being repeated. Repeat count: {repeat_count}")
                    print(duration_ms)
                    log_song_to_csv(f"{song_name}", artist_name, duration_ms)

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
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")
