import pandas as pd
import os

def calculate_response_time(df: pd.DataFrame, year: int, month: int=None) -> str:
    df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
    df['Year'] = df['tdate'].dt.year
    df['Month'] = df['tdate'].dt.month
    df = df[df['Year'] == year]
    if month is not None:
        df = df[df['Month'] == month]
    df['disptime'] = df['disptime'].astype(str).str[:5]  #  HH:MM
    df['enrtime'] = df['enrtime'].astype(str).str[:5] 
    
    df['disptime_dt'] = pd.to_datetime(df['tdate'].astype(str) + ' ' + df['disptime'], format='%Y-%m-%d %H:%M', errors='coerce')
    df['enrtime_dt'] = pd.to_datetime(df['tdate'].astype(str) + ' ' + df['enrtime'], format='%Y-%m-%d %H:%M', errors='coerce')

    response_time = []
    for index, row in df.iterrows():
        if pd.notna(row['disptime_dt']) and pd.notna(row['enrtime_dt']):
            if row['enrtime_dt'] < row['disptime_dt']:
                response_time.append(row['enrtime_dt'] + pd.Timedelta(days=1) - row['disptime_dt'])
            else:
                response_time.append(row['enrtime_dt'] - row['disptime_dt'])
        else:
            response_time.append(pd.NaT)

    df['response_time'] = response_time
    mean_response_time = df['response_time'].mean()
    if pd.isna(mean_response_time):
        return "N/A"
    print('mean_response_time',mean_response_time)
    return str(mean_response_time)