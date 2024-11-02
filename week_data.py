import pandas as pd

# Read the CSV file
df = pd.read_csv('listening_history.csv', names=['time', 'song', 'artist', 'listen_ms'])

# Convert the 'time' column to datetime
df['time'] = pd.to_datetime(df['time'])

# Group by weeks using pd.Grouper, summing the listen_ms (duration) and counting the songs
weekly_group = df.groupby([pd.Grouper(key='time', freq='W'), 'song', 'artist']).agg({
    'song': 'count',         
    'listen_ms': 'sum'       
}).rename(columns={'song': 'songs_played', 'listen_ms': 'total_listen_ms'})  # Rename for clarity

weekly_group['total_listen_min'] = weekly_group['total_listen_ms'] / 60000
weekly_group['total_listen_min'] = weekly_group['total_listen_min'].round(2)
weekly_group = weekly_group.sort_values(by='total_listen_min', ascending=False)
# Print the weekly grouped data
print(weekly_group)

weekly_group.to_csv('weekly.csv', encoding='utf-8')