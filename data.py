import pandas as pd

# Load the CSV data
df = pd.read_csv('listening_history.csv', header=None, names=['time', 'song', 'artist', 'duration'])

# Convert the 'time' column to datetime
df['time'] = pd.to_datetime(df['time'])

# Extract the date from the 'time' column
df['date'] = df['time'].dt.date

# Group by 'date' and 'song', counting occurrences
grouped = df.groupby(['date', 'song', 'artist']).agg(count=('time', 'size'), duration=('duration', 'first')).reset_index()

# Calculate total listen time in milliseconds
grouped['listen_time'] = grouped['duration'] * grouped['count']

# Convert listen_time to minutes
grouped['listen_time_minutes'] = grouped['listen_time'] / 60000
grouped['listen_time_minutes'] = grouped['listen_time_minutes'].round(2)

# Sort by 'count' in descending order and reset the index
sorted_grouped = (grouped
                  .sort_values(by='count', ascending=False)
                  .drop(['listen_time', 'duration'], axis=1)
                  .reset_index(drop=True)
                 )

# Start the index from 1
sorted_grouped.index += 1

# Display the sorted DataFrame
print(sorted_grouped)

sorted_grouped.to_csv('data.csv', index=False, header='True', encoding='utf-8')
