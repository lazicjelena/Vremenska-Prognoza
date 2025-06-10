# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 09:25:44 2025

@author: lazicjele
"""

#import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


''' Read Data '''

meteostat_data_path = os.path.join('data', 'export.csv')
openmeteo_data_path = os.path.join('data', 'open-meteo-44.81N20.46E120m.csv')
visualcrossing_data_path = os.path.join('data', 'belgrade.csv')
gfs_data_path = os.path.join('data', 'gfs.csv')

meteostat_df = pd.read_csv(meteostat_data_path)
openmeteo_df = pd.read_csv(openmeteo_data_path)
visualcross_df  = pd.read_csv(visualcrossing_data_path)
gfs_df = pd.read_csv(gfs_data_path)

openmeteo_df = openmeteo_df.rename(columns={
    'latitude': 'time',
    'longitude': 'temp'
})


openmeteo_df = openmeteo_df[['time', 'temp']][2:380]
openmeteo_df = openmeteo_df.reset_index(drop=True)
openmeteo_df['time'] = pd.to_datetime(openmeteo_df['time'], errors='coerce')

visualcross_df = visualcross_df.rename(columns={
    'datetime': 'time'
})

visualcross_df  = visualcross_df [['time', 'temp']]
visualcross_df['time'] = pd.to_datetime(visualcross_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')


meteostat_df['time'] = pd.to_datetime(meteostat_df['time'])

''' Svodjenje Openstat temperatura na jednu dnevno '''

def format_data_frame_time(meteo_df, meteostat_df):
    
    av_temp = []
    date_list = []
    
    for date in meteostat_df['time']:
        date_list.append(date)
        day_df = meteo_df[meteo_df['time'] == str(date)].copy()
        day_df['temperature_float'] = day_df['temp'].astype(float)
        
        av_temp.append(np.mean(day_df['temperature_float']))
        
        
    meteo_df_formated = pd.DataFrame({
        'time': date_list,
        'temp': av_temp
                })   
    
    return meteo_df_formated

meteostat_df_formated = format_data_frame_time(meteostat_df, visualcross_df)
openmeteo_df_formated = format_data_frame_time(openmeteo_df, visualcross_df)
gfs_df_formated = format_data_frame_time(gfs_df, visualcross_df)

''' Plot Data '''

# RMSE
rmse_mo = np.sqrt(np.mean((meteostat_df_formated['temp'] - openmeteo_df_formated['temp']) ** 2))
print(f"RMSE difference between Meteostat and Openmeteo is {rmse_mo:.2f}.")
rmse_mv = np.sqrt(np.mean((meteostat_df_formated['temp'] - visualcross_df['temp']) ** 2))
print(f"RMSE difference between Meteostat and Visualvross is {rmse_mv:.2f}.")
rmse_ov = np.sqrt(np.mean((visualcross_df['temp'] - openmeteo_df_formated['temp']) ** 2))
print(f"RMSE difference between Visualcross and Openmeteo is {rmse_ov:.2f}.")

plt.figure(figsize=(10, 6))
plt.plot(meteostat_df_formated['time'], meteostat_df_formated['temp'], label='Meteostat', color='red')
plt.plot(openmeteo_df_formated['time'], openmeteo_df_formated['temp'], label='Openmeteo', color='orange')
plt.plot(visualcross_df['time'], visualcross_df['temp'], label='Visualcross', color='purple')
plt.plot(gfs_df_formated['time'], gfs_df_formated['temp'], label='GFS', color='blue')


# Oznake
plt.xlabel('Date', fontsize=20)
plt.ylabel('T [°C]', fontsize=20)
plt.title("Temperature Forecasting", fontsize=25)


x_ticks = np.linspace(0, len(visualcross_df['time']) - 1, 10, dtype=int)
tick_dates = visualcross_df['time'].iloc[x_ticks]

# Formatiranje datuma na x-osi
plt.gca().set_xticks(tick_dates)
tick_dates = pd.to_datetime(tick_dates)  # konverzija ako su stringovi
plt.gca().set_xticklabels(tick_dates.dt.strftime('%b %d'), fontsize=15)

# Y-osi font
plt.yticks(fontsize=15)


# Legenda i layout
plt.legend(fontsize=15)
plt.tight_layout()
plt.show()