# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 15:05:50 2025

@author: lazicjele
"""


import pandas as pd
import pdfplumber
import numpy as np
import os


original_data_path = os.path.join('data', 'Republika Srbija - Meteorološki godisnjak 1 - klimatoloki podaci - 2023.pdf')
pd_path = os.path.join('data', 'Republika Srbija - Meteorološki godisnjak - 2023.csv')

# funkcija koja izdvaja korisne temperature

def is_int_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def extract_temperature_data_for_pd(table, month):
    
    date_list = []
    max_temp = []
    min_temp = []
    
    morning_temp = []
    midday_temp = []
    evening_temp = []
    
    av_temp = []
    day = 1
    
    padavine = []
    
    padavine_info = False
    for i in range(0,len(table)):
        print(i)
        rows = table[i][0].split('\n')
        
        if not padavine_info:
            # izdvoji jedan dan
            for row in rows:
    
                # izdvoji pojedinacne temperature
                day_temperatures = row.split(' ')
                
                if not is_int_string(day_temperatures[0]):
                    continue
                
                date_list.append(f"{day}.{month}.2023")
                day += 1
                
                max_temp.append(float(day_temperatures[5].replace(',','.'))) # maksimalna
                min_temp.append(float(day_temperatures[6].replace(',','.'))) # minimalna
                
                morning_temp.append(float(day_temperatures[9].replace(',','.'))) # temperatura u 7 h
                midday_temp.append(float(day_temperatures[10].replace(',','.'))) # temepratura u 14 h
                evening_temp.append(float(day_temperatures[11].replace(',','.'))) # temperatura u 21 h
    
                av_temp.append(float(day_temperatures[12].replace(',','.'))) # srednja temperatura
                
            if 'Д Напон водене паре Правац и брзина ветра Инсо- Облачност Пада- Снег Појаве' in rows:
                padavine_info = True
                day = 1
                
        else:
            
            for row in rows:
    
                # izdvoji pojedinacne temperature
                day_temperatures = row.split(' ')
                
                if not is_int_string(day_temperatures[0]):
                    continue
                
                date_list.append(f"{day}.{month}.2023")
                day += 1
                
                
                if day_temperatures[17] == '.':
                    padavine.append(np.NaN)
                else:
                    padavine.append(float(day_temperatures[17].replace(',','.'))) # srednja temperatura
            
        
            
    return  date_list, max_temp, min_temp, morning_temp, midday_temp, evening_temp, av_temp, padavine
            


''' Citanje podataka iz pdf dokumenta '''

# Prazan DataFrame pre petlje
df_all = pd.DataFrame(columns=[
    'date', 'max_temp', 'min_temp', 
    'morning_temp', 'midday_temp', 'evening_temp', 'av_temp', 'padavine'
])


with pdfplumber.open(original_data_path) as pdf:
    page_num = 0
    
    for page in pdf.pages:
        if page_num >= 40 and page_num <= 51: #
            table = page.extract_table()
            date_list, max_temp, min_temp, morning_temp, midday_temp, evening_temp, av_temp, padavine = extract_temperature_data_for_pd(table, page_num - 39)
                
            # Kreiranje DataFrame-a
            df_page = pd.DataFrame({
                'date': date_list,
                'max_temp': max_temp,
                'min_temp': min_temp,
                'morning_temp': morning_temp,
                'midday_temp': midday_temp,
                'evening_temp': evening_temp,
                'av_temp': av_temp,
                'padavine': padavine
            })
            
            # Dodavanje u glavni DataFrame
            df_all = pd.concat([df_all, df_page], ignore_index=True)
        
        page_num += 1

df_all['date'] = pd.to_datetime(df_all['date'], dayfirst=True, errors='coerce').dt.date
df_all.to_csv(pd_path, index = False)

