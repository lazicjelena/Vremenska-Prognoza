# -*- coding: utf-8 -*-
"""
Created on Tue May  6 11:32:14 2025

@author: lazicjele
"""

from datetime import datetime
import xarray as xr
import numpy as np
import requests
import os


# Funkcija za preuzimanje fajla
def download_grib_file(forecast_hour, date, base_url):
    # Datum koji se šalje kao argument pretvaramo u odgovarajući format
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")  # Pretvara u format YYYYMMDD

    leftlon = 19.8
    rightlon = 21.5
    toplat = 45.0
    bottomlat=44.2

    # Formiranje URL-a sa dinamičkim datumom
    #url = f"{base_url}?file=gfs.t00z.pgrb2.0p25.f{forecast_hour:03d}&lev_2_m_above_ground=on&var_TMAX=on&var_TMIN=on&var_TMP=on&subregion=&leftlon={leftlon}&rightlon={rightlon}&toplat={toplat}&bottomlat={bottomlat}&dir=%2Fgfs.{formatted_date}%2F00%2Fatmos"
    url = (
        f"{base_url}?file=gfs.t00z.pgrb2.0p25.f{forecast_hour:03d}"
        f"&lev_2_m_above_ground=on"
        f"&lev_surface=on" 
        f"&var_TMAX=on&var_TMIN=on&var_TMP=on"
        f"&var_APCP=on" 
        f"&leftlon={leftlon}&rightlon={rightlon}"
        f"&toplat={toplat}&bottomlat={bottomlat}"
        f"&dir=%2Fgfs.{formatted_date}%2F00%2Fatmos"
    )

    # Preuzimanje fajla
    response = requests.get(url)
    if response.status_code == 200:
        filename = f"gfs_{formatted_date}_f{forecast_hour:03d}.grib2"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Fajl za {forecast_hour}h preuzet.")
        return filename
    else:
        print(f"Greška pri preuzimanju fajla za {forecast_hour}h.")
        return None
    
    
# Učitavanje i analiza podataka
def load_temperature_data(file_path):
    ds = xr.open_dataset(file_path, engine='cfgrib', filter_by_keys={'typeOfLevel': 'heightAboveGround'})
    print(ds.data_vars)
    return ds['t2m']



def load_temperature_data_minmax(file_path, latitude_beograd, longitude_beograd):
    ds = xr.open_dataset(file_path, engine='cfgrib')

    tmax = ds['tmax'].sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest') - 273.15 if 'tmax' in ds else None
    tmin = ds['tmin'].sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest') - 273.15 if 'tmin' in ds else None

    return {
        'tmax': tmax.values.item() if tmax is not None else None,
        'tmin': tmin.values.item() if tmin is not None else None
    }


def load_precipitation(file_path, latitude, longitude):
    try:
        ds = xr.open_dataset(file_path, engine='cfgrib')
        
        if 'tp' in ds:
            apcp = ds['tp'].sel(latitude=latitude, longitude=longitude, method='nearest')
            return apcp.values.item()
        else:
            return None
    except Exception as e:
        print(f"Greška pri čitanju APCP: {e}")
        return None


# Postavljanje parametara
base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
# Definisanje parametara
latitude_beograd = 44.8176
longitude_beograd = 20.4633
#forecast_steps = [0, 3, 6, 9, 12, 15, 18, 21]  # Primer vremenskih koraka u satima
forecast_steps = range(3, 24*30, 3)
temperatures = []
precipitations = []
date = "2025-05-07"  # Datum za 5. maj 2025. godine -> zelim za naredna 3 dana

# Definisanje direktorijuma za preuzete fajlove
download_dir = f"gfs_data_{date}"  # Kreira se direktorijum sa imenom prema datumu

# Pravimo direktorijum ako ne postoji
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
    
# Preuzimanje i učitavanje podataka za sve korake prognoze
for forecast_hour in forecast_steps:
    file_path = download_grib_file(forecast_hour, date, base_url)  # Dodajemo datum kao argument
    
    if file_path:
        new_file_path = os.path.join(download_dir, os.path.basename(file_path))
        os.rename(file_path, new_file_path)  # Premesti fajl
        
        temp_data = load_temperature_data(new_file_path)
        temp_at_beograd = temp_data.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
        temperature_celsius = temp_at_beograd.values - 273.15  # Konvertovanje u Celsius
        r = load_temperature_data_minmax(new_file_path, latitude_beograd, longitude_beograd)
        print(r['tmax'])
        temperatures.append(temperature_celsius)
        
        precip = load_precipitation(new_file_path, latitude_beograd, longitude_beograd)
        print("Padavine:", precip)
        precipitations.append(precip)

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


output_file_path = os.path.join('data', 'gfs.csv')
df.to_csv(output_file_path, index = False)