#!/usr/bin/python
# -*- coding: utf-8 -*-
#from gurobipy import *
import pandas as pd
import graph
import postgis_database
from pre_processamento import PreProcessamento
import datetime
from tqdm import tqdm

inicio = datetime.datetime.now()
database = postgis_database.Database()

profile_limit = 10  # recomendable amount of missing people
raio = 150  # radius profile selection
raio_max = 150

# Reads missing people from CSV
missing_dataset = pd.read_csv('dataset/desaparecidos_BA.csv', header=0, encoding='latin-1')
#missing_dataset = pd.read_csv('dataset/1000_desaparecidos_lat_lon.csv', header=0, encoding='latin-1')

# Reads twitter profile from CSV
g = graph.Graph('dataset/profiles_BA.csv')
#g = graph.Graph('dataset/500_profile_lat_lon.csv')

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

    if raio_max < raio_missing[index_j]:
        raio_max = raio_missing[index_j]

    arr_network[index_j] = database.select_network_profiles(arr_profile_missing_area[index_j])
    arr_network[index_j] = arr_profile_missing_area[index_j]
    database.insert_raio_missing(index_j, raio_missing[index_j])

    for network_index_i in arr_network[index_j]:
        try:
            if index_j not in var_r[network_index_i]:
                var_r[network_index_i].append(index_j)
        except:
            var_r[network_index_i] = []
            var_r[network_index_i].append(index_j)

# Model Start
m = Model('missing')

print("\n Creating ri_j and R2")
for index_i in tqdm(var_r):
    expr_R2 = LinExpr()
    for r_index_j in var_r[index_i]:
        expr_R2 += m.addVar(vtype=GRB.BINARY, name='r[' + str(index_i) + '][' + str(r_index_j) + ']')
    m.addConstr(expr_R2 <= profile_limit, 'R2_i' + str(index_i))

m.update()

check_dkj = {}
print("\n Creating dk_j, dj, R1, R3 e R4")
inicio_restricoes = datetime.datetime.now()
expr_obj = LinExpr()
for index_j in tqdm(missing_index):
    missing = database.select_missing(index_j)
    d_j = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='d[' + str(index_j) + ']')
    expr_obj += d_j

    arr_index_k = []
    expr_R3 = LinExpr()

    for network_index_k in arr_network[index_j]:
        profile = database.select_profile(network_index_k)

        d_k_j = m.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS,
                         name='d[' + str(network_index_k) + '][' + str(index_j) + ']')

        g_kj = database.select_distance_with_raio_max(missing['latitude'], missing['longitude'], profile['latitude'],
                                        profile['longitude'], raio_max)

        #g_kj = database.select_distance(missing['latitude'], missing['longitude'], profile['latitude'],
                                                      #profile['longitude'])
        expr_R3 += g_kj * d_k_j

        expr_R4 = LinExpr()
        arr_influencers = database.select_influences_by_influenced(network_index_k)
        # for index_i in var_r:
        for index_i in arr_influencers:
            if index_i in arr_network[index_j]:
                try:
                    f_ik = database.select_influences(index_i, network_index_k)
                    expr_R4 += f_ik * m.getVarByName(
                        'r[' + str(index_i) + '][' + str(index_j) + ']')
                except:
                    pass
        m.addConstr(expr_R4 >= d_k_j, 'R4_j' + str(index_j) + '_k' + str(network_index_k))
    m.addConstr(expr_R3 == d_j, 'R3_j' + str(index_j))

    expr_R1 = LinExpr()
    for r_index_i in var_r:
        if len(var_r[r_index_i]) > 0:
            try:
                r_i_j = m.getVarByName('r[' + str(r_index_i) + '][' + str(index_j) + ']')
                expr_R1 += r_i_j
            except:
                pass

    m.addConstr(expr_R1 <= 1, 'R1_j' + str(index_j))

fim_restricoes = datetime.datetime.now()
print('TEMPO DE EXECUÇÃO RESTIÇÕES: ' + str(fim_restricoes - inicio_restricoes))

m.setObjective(expr_obj, GRB.MAXIMIZE)

#### optimize
print("\n Optimizing ...")
inicio_modelo = datetime.datetime.now()
m.optimize()
fim_modelo = datetime.datetime.now()
print('TEMPO DE EXECUÇÃO MODELO: ' + str(fim_modelo - inicio_modelo))

fim = datetime.datetime.now()
print('\n TEMPO DE EXECUÇÃO: ' + str(fim - inicio))

#### print results
print('\n Print Results')
print('Obj:' + str(m.objVal))
print('Quality: ' + str(m.printQuality()))

#### export results
print('\n Export Results')
m.write('resultados/model.lp')
file = open('resultados/resultado.txt', 'w')
file_variaveis = open('resultados/variaveis_maiores_0.txt', 'w')
file.write('tempo execuçãp:' + str(fim - inicio) + '\n')
file.write('Obj:' + str(m.objVal) + '\n')
file.write('Variaveis \n')
for v in m.getVars():
    if v.x > 0:
        file_variaveis.write(v.varName + ':' + str(v.x) + '\n')
    file.write(v.varName + ':' + str(v.x) + '\n')
file.close()
file_variaveis.close()

##############################
print('\n Insert results in Database')
inicio_database = datetime.datetime.now()
database.delete_all_result_r()
database.delete_all_result_dj()
database.delete_all_result_dkj()
arr_index_j = []
for index_i in tqdm(var_r):
    for r_index_j in var_r[index_i]:
        if r_index_j not in arr_index_j:
            arr_index_j.append(r_index_j)
            # get d_j
            try:
                d = m.getVarByName('d[' + str(r_index_j) + ']')
                database.insert_result_dj(r_index_j, d.x)
            except:
                pass

        # get r_ij
        try:
            r = m.getVarByName('r[' + str(index_i) + '][' + str(r_index_j) + ']')
            database.insert_result_r(index_i, r_index_j, r.x)
        except:
            pass

        # get d_kj
        try:
            d = m.getVarByName('d[' + str(index_i) + '][' + str(r_index_j) + ']')
            database.insert_result_dkj(index_i, r_index_j, d.x)
        except:
            pass
fim_database = datetime.datetime.now()
print('TEMPO DE EXECUÇÃO DATABASE: ' + str(fim_database - inicio_database))
print('\n Close database connection...')
database.close_connection()
