# -*- coding: utf-8 -*-
"""
Created on Tue May 13 11:27:41 2025

@author: lazicjele
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May  6 14:54:51 2025

@author: lazicjele
"""
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import cfgrib
import os


latitude_beograd = 44.8176
longitude_beograd = 20.4633

# temp_bg = ds['t2m'].sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')

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
    

def load_meteorological_variables(file_path):
    results = {}
    
    # 1. Temperatura
    try:
        ds_temp = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'heightAboveGround', 'level': 2})
        #print(ds_temp.data_vars)
        if 't2m' in ds_temp:
            results['t2m'] = ds_temp['t2m']
    except Exception as e:
        print(f"[temperatura 2m] Nije pronađena: {e}")
        
    # 2. Padavine (total precipitation) - surface level
    try:
        ds_tp = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'surface'})
        #print(ds_tp.data_vars)
        if 'tp' in ds_tp:
            results['tp'] = ds_tp['tp']
    except Exception as e:
        print(f"[padavine] Nije pronađena: {e}")

    # 3. Vlažnost (relativna) na 2 metra
    try:
        ds_rh = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'heightAboveGround', 'level': 2})
        if 'r2' in ds_rh:
            results['r2'] = ds_rh['r2']
    except Exception as e:
        print(f"[vlažnost 2m] Nije pronađena: {e}")

    # 4. Broj suncanih sati
    try:
        ds_ssrd = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'surface'})
        if 'sdswrf' in ds_ssrd:
            results['sdswrf'] = ds_ssrd['sdswrf']
    except Exception as e:
        print(f"[Broj osuncanih sati] Nije pronađena: {e}")

    # 5. Padavine (total precipitation) - surface level
    try:
        ds_tp = cfgrib.open_dataset(file_path, filter_by_keys={'typeOfLevel': 'surface'})
        #print(ds_tp.data_vars)
        if 'crain' in ds_tp:
            results['crain'] = ds_tp['crain']
    except Exception as e:
        print(f"[padavine kisa] Nije pronađena: {e}")

    return results


def download_data_for_ten_days(date):
        
    # Definisanje parametara
    latitude_beograd = 44.8176
    longitude_beograd = 20.4633
    forecast_steps = range(3, 24*10, 3)
    temperatures = []
    precipitations = []
    vlaznost = []
    osuncani_sati = []
    kisa = []
    
    
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
            results = load_meteorological_variables(new_file_path)
            
            temp_data = results['t2m']
            temp_at_beograd = temp_data.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
            temperature_celsius = temp_at_beograd.values - 273.15  # Konvertovanje u Celsius
            print("Temperatura:", temperature_celsius)
            temperatures.append(temperature_celsius)
            
            precip = results['tp']
            precip_at_belgrade = precip.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
            print("Padavine:", precip_at_belgrade.values)
            precipitations.append(precip_at_belgrade.values)
            
            relativna_vlaznost = results['r2']
            relativna_vlaznost_at_belgrade = relativna_vlaznost.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
            print("Relativna vlaznost vazduha", relativna_vlaznost_at_belgrade.values)
            vlaznost.append(relativna_vlaznost_at_belgrade.values)
              
            broj_osuncanih_sati = results['sdswrf']
            broj_osuncanih_sati_at_belgrade = broj_osuncanih_sati.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
            print("Broj osuncanih sati", broj_osuncanih_sati_at_belgrade.values)
            osuncani_sati.append(broj_osuncanih_sati_at_belgrade.values)
            
            padavine_kisa = results['crain']
            padavine_kisa_at_belgrade = padavine_kisa.sel(latitude=latitude_beograd, longitude=longitude_beograd, method='nearest')
            print("Padavine kisa", padavine_kisa_at_belgrade.values)
            kisa.append(padavine_kisa_at_belgrade.values)
            
            os.remove(new_file_path)  # Brisanje fajla nakon učitavanja
        else:
            temperatures.append(np.nan)
            precipitations.append(np.nan)
            kisa.append(np.nan)
            osuncani_sati.append(np.nan)
            vlaznost.append(np.nan)
            
    
        ''' Cuvanje podataka u csv fajlu '''
    
    
    start_date = pd.to_datetime(date)
    output_file_path = os.path.join('data', 'vremenski podaci', f"{date}.csv")
        # Create list of timestamps by adding hours
    tick_dates = [start_date + pd.Timedelta(hours=i) for i in forecast_steps]
        
    df = pd.DataFrame({
        'time': tick_dates,
        'temp': temperatures,
        'prcp': precipitations,
        'solar radiation': osuncani_sati,
        'relative humidity': vlaznost,
        'prcp_rain': kisa
        })
                
    df.to_csv(output_file_path, index = False)
        
    return
    
start_date = "2023-05-1"
end_date = "2023-09-01"

# Parsiranje stringova u datumske objekte
start = datetime.strptime(start_date, "%Y-%m-%d")
end = datetime.strptime(end_date, "%Y-%m-%d")

# Koračamo po danima (može i po 10 ako želiš da ne preklapaš)
current = start
while current <= end:
    date_str = current.strftime("%Y-%m-%d")
    print(f"Preuzimam podatke za: {date_str}")
    download_data_for_ten_days(date_str)  # Tvoja funkcija
    current += timedelta(days=10)  # ili 10 ako želiš da se ne preklapa