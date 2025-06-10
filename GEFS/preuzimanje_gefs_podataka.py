# -*- coding: utf-8 -*-
"""
Created on Tue May  6 14:54:51 2025

@author: lazicjele
"""
import os
import requests
# import xarray as xr
import numpy as np
import cfgrib
from datetime import datetime, timedelta


file_path  = os.path.join('data', 'samples', 'geavg.t00z.pgrb2a.0p50.f000')
ds = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'heightAboveGround'})
print(ds.data_vars)

ds2 = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'surface'})
print(ds2.data_vars)

#precipitable water
ds3 = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'atmosphereSingleLayer'})
print(ds3.data_vars)

latitude_beograd = 44.8176
longitude_beograd = 20.4633

temp_bg = ds['t2m'].sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')

def download_grib_files(date, forecast_hour=6):
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
    forecast_hour_str = f"{int(forecast_hour):03d}"

    base_url = "https://noaa-gefs-pds.s3.amazonaws.com/gefs."
    url = f"{base_url}{formatted_date}/00/atmos/pgrb2ap5/geavg.t00z.pgrb2a.0p50.f{forecast_hour_str}"

    response = requests.get(url)
    if response.status_code == 200:
        filename = f"gefs_{formatted_date}_f{forecast_hour_str}.grib2"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Fajl za {forecast_hour_str} preuzet.")
        return filename
    else:
        print(f"Greška pri preuzimanju fajla za {forecast_hour_str}. HTTP status: {response.status_code}")
        return None
    
# Učitavanje i analiza podataka
def load_temperature_data(file_path):
    ds = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'heightAboveGround'})
    print(ds.data_vars)

    return ds['t2m']


def load_precipitation(file_path):
    ds = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'surface'})
    print(ds.data_vars)

    # Vraća padavine ako postoji varijabla 'tp'
    if 'tp' in ds.data_vars:
        return ds['tp']
    else:
        raise ValueError("Varijabla 'tp' (total precipitation) nije pronađena u datasetu.")
    
# Definisanje parametara
latitude_beograd = 44.8176
longitude_beograd = 20.4633
#forecast_steps = [0, 3, 6]  # Primer vremenskih koraka u satima
forecast_steps = range(3, 24*3, 3)
temperatures = []
precipitations = []
date = "2024-01-01"  # Datum za 6. maj 2025. godine -> zelim za naredna 3 dana

# Definisanje direktorijuma za preuzete fajlove
download_dir = f"gefs_data_{date}"  # Kreira se direktorijum sa imenom prema datumu

# Pravimo direktorijum ako ne postoji
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


# Preuzimanje i učitavanje podataka za sve korake prognoze
for forecast_hour in forecast_steps:
    file_path = download_grib_files(date, forecast_hour)  # Dodajemo datum kao argument
    if file_path:
        new_file_path = os.path.join(download_dir, os.path.basename(file_path))
        os.rename(file_path, new_file_path)  # Premesti fajl
        temp_data = load_temperature_data(new_file_path)

        temp_at_beograd = temp_data.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
        temperature_celsius = temp_at_beograd.values - 273.15  # Konvertovanje u Celsius
        temperatures.append(temperature_celsius)
        
        precip_data = load_precipitation(new_file_path)
        precip_at_belgrade = precip_data.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
        print("Padavine:", precip_at_belgrade.values)
        precipitations.append(precip_at_belgrade.values)

        os.remove(new_file_path)  # Brisanje fajla nakon učitavanja
    else:
        temperatures.append(np.nan)
        precipitations.append(np.nan)

''' Cuvanje podataka u csv fajlu '''
import pandas as pd

start_date = pd.to_datetime(date)
# Create list of timestamps by adding hours
tick_dates = [start_date + pd.Timedelta(hours=i) for i in forecast_steps]

df = pd.DataFrame({
    'time': tick_dates,
    'temp': temperatures,
    'prcp': precipitations
})


output_file_path = os.path.join('data', 'gefs.csv')
#df.to_csv(output_file_path, index = False)