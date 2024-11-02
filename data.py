import pandas as pd

# Debug prints
DEBUG = True

def sort_by_day(grouped) -> None:
    # Get top 5 songs by listen time for each day
    top_5_per_day = (grouped
                     .groupby('date', as_index=False, group_keys=False)
                     .apply(lambda x: x.nlargest(5, 'listen_time_minutes'))
                     .reset_index(drop=True))

    if DEBUG:
        print("Top 5 Songs by Day:")
        print(top_5_per_day)

    # Save daily data to CSV
    top_5_per_day.to_csv('data_day.csv', index=False, header=True, encoding='utf-8')

def sort_by_week(grouped) -> None:
    # Group by 'year', 'week', 'song', 'artist' and aggregate counts and listening time per week
    weekly_grouped = (grouped
                      .groupby(['year', 'week', 'song', 'artist'], as_index=False)
                      .agg(
                          count=('count', 'sum'),
                          listen_time_minutes=('listen_time_minutes', 'sum').round(2)
                      )
                      .sort_values(by=['year', 'week', 'listen_time_minutes'], ascending=[False, False, False])
                     )

    # Get the top 5 songs for each week by listen time
    top_5_per_week = (weekly_grouped
                      .groupby(['year', 'week'], as_index=False, group_keys=False)
                      .apply(lambda x: x.nlargest(5, 'listen_time_minutes'))
                      .reset_index(drop=True)
                     )

    if DEBUG:
        print("Top 5 Songs by Week:")
        print(top_5_per_week)

    # Save weekly data to CSV
    top_5_per_week.to_csv('data_week.csv', index=False, header=True, encoding='utf-8')

def sort_by_month(grouped) -> None:
    # Group by 'year', 'month', 'song', 'artist' and aggregate counts and listening time per month
    monthly_grouped = (grouped
                       .groupby(['year', 'month', 'song', 'artist'], as_index=False)
                       .agg(
                           count=('count', 'sum'),
                           listen_time_minutes=('listen_time_minutes', 'sum').round(2)
                       )
                       .sort_values(by=['year', 'month', 'listen_time_minutes'], ascending=[False, False, False])
                      )

    # Get the top 5 songs for each month by listen time
    top_5_per_month = (monthly_grouped
                       .groupby(['year', 'month'], as_index=False, group_keys=False)
                       .apply(lambda x: x.nlargest(5, 'listen_time_minutes'))
                       .reset_index(drop=True)
                      )

    if DEBUG:
        print("Top 5 Songs by Month:")
        print(top_5_per_month)

    # Save monthly data to CSV
    top_5_per_month.to_csv('data_month.csv', index=False, header=True, encoding='utf-8')

if __name__ == '__main__':
    try:
        df = pd.read_csv('listening_history.csv', header=None, names=['time', 'song', 'artist', 'duration'])

        # Convert 'time' to datetime and handle errors
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df = df.dropna(subset=['time'])  # Drop rows where 'time' couldn't be parsed

        # Extract date, year, week, and month
        df['date'] = df['time'].dt.date
        df['year'] = df['time'].dt.year
        df['week'] = df['time'].dt.isocalendar().week
        df['month'] = df['time'].dt.month

        # Group by date, song, artist to get daily counts and total listen times
        grouped = df.groupby(['date', 'song', 'artist']).agg(
            count=('time', 'size'),
            total_duration=('duration', 'sum')
        ).reset_index()

        # Add week and month columns to grouped data
        grouped = grouped.merge(df[['date', 'year', 'week', 'month']].drop_duplicates(), on='date')

        # Convert listen time to minutes
        grouped['listen_time_minutes'] = grouped['total_duration'] / 60000
        grouped['listen_time_minutes'] = grouped['listen_time_minutes'].round(2)
        
        # Generate and save daily, weekly, and monthly summaries
        sort_by_day(grouped)
        sort_by_week(grouped)
        sort_by_month(grouped)

    except Exception as e:
        print(f'Error trying to read the csv and converting the time: {e}')
