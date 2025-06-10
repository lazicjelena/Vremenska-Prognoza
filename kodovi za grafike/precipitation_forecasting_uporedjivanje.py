# -*- coding: utf-8 -*-
"""
Created on Tue May  6 14:15:59 2025

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
gefs_data_path = os.path.join('data', 'gefs.csv')


meteostat_df = pd.read_csv(meteostat_data_path)
openmeteo_df = pd.read_csv(openmeteo_data_path)
visualcross_df  = pd.read_csv(visualcrossing_data_path)
gfs_df = pd.read_csv(gfs_data_path)
gefs_df = pd.read_csv(gefs_data_path)

openmeteo_df = openmeteo_df.rename(columns={
    'latitude': 'time',
    'longitude': 'temp',
    'elevation': 'prcp'
})


openmeteo_df = openmeteo_df[['time', 'temp', 'prcp']][2:380]
openmeteo_df = openmeteo_df.reset_index(drop=True)
openmeteo_df['time'] = pd.to_datetime(openmeteo_df['time'], errors='coerce')

visualcross_df = visualcross_df.rename(columns={
    'datetime': 'time',
    'precip': 'prcp'
})

visualcross_df  = visualcross_df [['time', 'temp', 'prcp']]
visualcross_df['time'] = pd.to_datetime(visualcross_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')


meteostat_df['time'] = pd.to_datetime(meteostat_df['time'])


''' Svodjenje Openstat temperatura na jednu dnevno '''

def format_data_frame_time(data, ref_data_df):
    
    av_temp = {
        'temp': [],
        'prcp': []
        }
    date_list = []
    
    for date in ref_data_df['time']:
        date_list.append(date)
        day_df = data[data['time'] == str(date)].copy()
            
        for column_name in ['temp', 'prcp']:
            day_df[f'{column_name}_float'] = day_df[column_name].astype(float)
        
            av_temp[column_name].append(np.mean(day_df[f'{column_name}_float']))
        
        
    data_formated = pd.DataFrame({
        'time': date_list,
        'temp': av_temp['temp'],
        'prcp': av_temp['prcp']
                })   
    
    data_formated['prcp'] = data_formated['prcp'].replace(0, np.nan)
    
    return data_formated

meteostat_df_formated = format_data_frame_time(meteostat_df, visualcross_df)
openmeteo_df_formated = format_data_frame_time(openmeteo_df, visualcross_df)
gfs_df_formated = format_data_frame_time(gfs_df, visualcross_df)
gefs_df_formated = format_data_frame_time(gefs_df, visualcross_df)

''' Plot Precipitation Data '''

plt.figure(figsize=(10, 6))
plt.scatter(meteostat_df['time'], meteostat_df['prcp'], label='Meteostat', color='red')
plt.scatter(openmeteo_df_formated['time'], openmeteo_df_formated['prcp'], label='Openmeteo', color='orange')
plt.scatter(visualcross_df['time'], visualcross_df['prcp'], label='Visualcross', color='purple')
plt.scatter(gfs_df_formated['time'], gfs_df_formated['prcp'], label='GFS', color='blue')
plt.scatter(gefs_df_formated['time'], gefs_df_formated['prcp'], label='GEFS', color='green')

# Oznake
plt.xlabel('Date', fontsize=20)
plt.ylabel('Precipitation [mm]', fontsize=20)
plt.title("Precipitation Forecasting", fontsize=25)


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


''' Plot Temperature Data '''

plt.figure(figsize=(10, 6))
plt.plot(meteostat_df_formated['time'], meteostat_df_formated['temp'], label='Meteostat', color='red')
plt.plot(openmeteo_df_formated['time'], openmeteo_df_formated['temp'], label='Openmeteo', color='orange')
plt.plot(visualcross_df['time'], visualcross_df['temp'], label='Visualcross', color='purple')
#plt.plot(gfs_df_formated['time'], gfs_df_formated['temp'], label='GFS', color='blue')


gfs_valid_data = gfs_df_formated[gfs_df_formated['temp'].notna()]
plt.plot(gfs_valid_data['time'], gfs_valid_data['temp'], label='GEFS', color='blue')

gefs_valid_data = gefs_df_formated[gefs_df_formated['temp'].notna()]
plt.plot(gefs_valid_data['time'], gefs_valid_data['temp'], label='GEFS', color='green')

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