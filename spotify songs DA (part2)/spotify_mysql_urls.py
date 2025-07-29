import re
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import mysql.connector
# Set up Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='382f933b22ab4072835cbebb1b5edf99',
    client_secret='66c0c2181b94452fa56b5ac4b9a2e2d0'
))
# MySQL Database Connection
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '12345',
    'database': 'spotify_db'
}
# Connect to the database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Read track URLs from file
file_path = "Hot Hits tamil.txt"
with open(file_path, 'r') as file:
    track_urls = file.readlines()

# Process each URL
for track_url in track_urls:
    track_url = track_url.strip()
    try:
        # Extract track ID
        track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)

        # Fetch from Spotify
        track = sp.track(track_id)

        # Extract metadata
        track_data = {
            'Track Name': track['name'],
            'Artist': track['artists'][0]['name'],
            'Album': track['album']['name'],
            'Popularity': track['popularity'],
            'Duration (minutes)': track['duration_ms'] / 60000
        }

        # Check if track already exists
        check_query = """
        SELECT COUNT(*) FROM spotify_tracks
        WHERE track_name = %s AND artist = %s
        """
        cursor.execute(check_query, (track_data['Track Name'], track_data['Artist']))
        result = cursor.fetchone()

        if result[0] == 0:
            # Insert new track
            insert_query = """
            INSERT INTO spotify_tracks (track_name, artist, album, popularity, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                track_data['Track Name'],
                track_data['Artist'],
                track_data['Album'],
                track_data['Popularity'],
                track_data['Duration (minutes)']
            ))
            connection.commit()
            print(f"Inserted: {track_data['Track Name']} by {track_data['Artist']}")
        else:
            print(f"Skipped (already exists): {track_data['Track Name']} by {track_data['Artist']}")

    except Exception as e:
        print(f"Error processing URL: {track_url}, Error: {e}")

# Close connection
cursor.close()
connection.close()

print("All tracks have been processed and inserted into the database.")
