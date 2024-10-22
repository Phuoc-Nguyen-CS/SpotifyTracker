import pandas as pd

# Debug prints
DEBUG = False

def sort_by_day(df) -> None:

    # Sort by 'count' in descending order and reset the index
    sorted_grouped = (grouped
                    .sort_values(by=['date', 'count', 'listen_time_minutes'], ascending=False)
                    .drop(['listen_time', 'duration'], axis=1)
                    .reset_index(drop=True)
                    )

    # Start the index from 1
    sorted_grouped.index += 1

    # Display the sorted DataFrame
    if DEBUG:
      print(sorted_grouped)   

    sorted_grouped.to_csv('data.csv', index=False, header='True', encoding='utf-8')

if __name__ == '__main__':
    # Load the CSV data and extract the date
    try:
        df = pd.read_csv('listening_history.csv', header=None, names=['time', 'song', 'artist', 'duration'])
        df['time'] = pd.to_datetime(df['time'])
        df['date'] = df['time'].dt.date
        grouped = df.groupby(['date', 'song', 'artist']).agg(
            count=('time', 'size'), 
            total_duration=('duration', 'sum')
            ).reset_index()

        # Convert listen_time to minutes
        grouped['listen_time_minutes'] = grouped['total_duration'] / 60000
        grouped['listen_time_minutes'] = grouped['listen_time_minutes'].round(2)
    except Exception as e:
        print('Error trying to read the csv and converting the time')
    