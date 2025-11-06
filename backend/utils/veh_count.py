import pandas as pd
import json


def calculate_veh_count(df: pd.DataFrame, year: int) -> json:
  df['tdate'] = pd.to_datetime(df['tdate'], errors='coerce')
  df['Year'] = df['tdate'].dt.year
  df = df[df['Year'] == year]
  df['Month'] = df['tdate'].dt.month
  grouped = df.groupby(['Month','veh']).size().reset_index(name='veh_count')
  data = []
  for veh, group in grouped.groupby('veh'):
      data.append({
          "id": veh,
          "data": [{"x": int(row['Month']), "y": int(row['veh_count'])} for _, row in group.iterrows()]
      })
  return data