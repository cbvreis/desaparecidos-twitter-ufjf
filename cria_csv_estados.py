# -*- coding: utf-8 -*-
import csv
import pandas as pd
from tqdm import tqdm

#################### CRIA ESTADOS
# profile_dataset = pd.read_csv('dataset/profile_lat_lon.csv', header=0, encoding='latin-1')
#
# csv_profile = csv.writer(open("dataset/profiles_BA.csv", "w"))
# csv_profile.writerow(['Perfil', 'Cidade', 'Seguidor', 'Peso', 'lon', 'lat'])
#
# for index, row in tqdm(profile_dataset.iterrows()):
#     try:
#         if "bahia" in row['Cidade']:
#             csv_profile.writerow([row['Perfil'], row['Cidade'], row['Seguidor'], row['Peso'], row['lon'], row['lat']])
#     except:
#         pass

#################### CRIA DESAPARECIDOS
missing_dataset = pd.read_csv('dataset/desaparecidos_lat_lon.csv', header=0, encoding='latin-1')

csv_desaparecidos = csv.writer(open("dataset/desaparecidos_AM.csv", "w"))
csv_desaparecidos.writerow(['estado', 'id', 'lon', 'lat'])
for index, row in tqdm(missing_dataset.iterrows()):
    try:
        if "Bahia" in row['estado']:
            csv_desaparecidos.writerow([row['estado'], row['id'], row['lon'], row['lat']])
    except:
        pass
