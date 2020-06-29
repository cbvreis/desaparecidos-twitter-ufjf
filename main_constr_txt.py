#!/usr/bin/python
# -*- coding: utf-8 -*-
from gurobipy import *
import pandas as pd
import graph
import postgis_database
from pre_processamento import PreProcessamento
import datetime
from tqdm import tqdm

inicio = datetime.datetime.now()
database = postgis_database.Database()

profile_limit = 2  # recomendable amount of missing people
raio = 150  # radius profile selection

# Reads missing people from CSV
missing_dataset = pd.read_csv('dataset/desaparecidos_RJ.csv', header=0, encoding='latin-1')
# missing_dataset = pd.read_csv('dataset/100_desaparecidos_lat_lon.csv', header=0, encoding='latin-1')

# Reads twitter profile from CSV
g = graph.Graph('dataset/profiles_RJ.csv')
# g = graph.Graph('dataset/500_profile_lat_lon.csv')

pre_processamento = PreProcessamento(database, g, missing_dataset)
print('Done!')

missing_index = pre_processamento.get_missing_index()
database.delete_all_raio_missing()
print('\n Check if rij will be created')
var_r = {}
person_region = {}
raio_missing = {}
arr_profile_missing_area = {}
arr_network = {}
for index_j in tqdm(missing_index):
    person_region[index_j] = 1
    arr_profile_missing_area[index_j], raio_missing[index_j] = database.select_profile_raio(index_j, raio,
                                                                                            person_region[index_j])

    arr_network[index_j] = database.select_network_profiles(arr_profile_missing_area[index_j])
    database.insert_raio_missing(index_j, raio_missing[index_j])

    for network_index_i in arr_network[index_j]:
        try:
            if index_j not in var_r[network_index_i]:
                var_r[network_index_i].append(index_j)
        except:
            var_r[network_index_i] = []
            var_r[network_index_i].append(index_j)

# Model Start
arq_R2 = open('file_txt/R2.txt', 'w')
print("\n Creating ri_j and R2")
for index_i in tqdm(var_r):
    arq_R2.write('R2_i ' + str(index_i) + '\n')
    for r_index_j in var_r[index_i]:
        arq_R2.write('r[' + str(index_i) + '][' + str(r_index_j) + ']\n')
arq_R2.close()

check_dkj = {}
print("\n Creating dk_j, dj, R1, R3 e R4")
inicio_restricoes = datetime.datetime.now()

arq_R1 = open('file_txt/R1.txt', 'w')
arq_R3 = open('file_txt/R3.txt', 'w')
arq_R4 = open('file_txt/R4.txt', 'w')
arq_Obj = open('file_txt/Obj.txt', 'w')
for index_j in tqdm(missing_index):
    missing = database.select_missing(index_j)
    arq_Obj.write('d[' + str(index_j) + ']\n')

    arr_index_k = []
    arq_R3.write('R3_j ' + str(index_j) + '\n')
    for network_index_k in arr_network[index_j]:
        profile = database.select_profile(network_index_k)

        g_kj = database.select_distance(missing['latitude'], missing['longitude'], profile['latitude'],
                                        profile['longitude'])

        arq_R3.write(str(g_kj) + ' * d[' + str(network_index_k) + '][' + str(index_j) + ']\n')

        arr_influencers = database.select_influences_by_influenced(network_index_k)
        arq_R4.write('R4_j ' + str(index_j) + ' k ' + str(network_index_k)+ '\n')
        for index_i in arr_influencers:
            try:
                f_ik = database.select_influences(index_i, network_index_k)
                arq_R4.write(str(f_ik) + ' * r[' + str(index_i) + '][' + str(index_j) + ']\n')
            except:
                pass

    arq_R1.write('R1_j ' + str(index_j) + '\n')
    for r_index_i in var_r:
        if len(var_r[r_index_i]) > 0:
            try:
                arq_R1.write('r[' + str(r_index_i) + '][' + str(index_j) + ']\n')
            except:
                pass

fim_restricoes = datetime.datetime.now()
print('TEMPO DE EXECUÇÃO RESTIÇÕES: ' + str(fim_restricoes - inicio_restricoes))

arq_R1.close()
arq_R3.close()
arq_R4.close()
arq_Obj.close()

fim = datetime.datetime.now()
print('\n TEMPO DE EXECUÇÃO: ' + str(fim - inicio))

print('\n Close database connection...')
database.close_connection()
