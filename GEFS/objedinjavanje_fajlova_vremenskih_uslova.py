# -*- coding: utf-8 -*-
"""
Created on Wed May 14 09:15:29 2025

@author: lazicjele
"""

import pandas as pd
import os
import glob

# Putanja do foldera sa CSV fajlovima
folder_path = os.path.join('data', 'vremenski podaci')

# Pronalazi sve .csv fajlove u folderu
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Čita sve fajlove i spaja ih u jedan DataFrame
df_list = [pd.read_csv(f) for f in csv_files]
merged_df = pd.concat(df_list, ignore_index=True)

# Prikazuje prvih nekoliko redova
print(merged_df.head())


output_file_path = os.path.join('data',  "vremenski_podaci.csv")
merged_df.to_csv(output_file_path, index = False)
