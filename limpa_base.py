#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import graph
import postgis_database
from pre_processamento import PreProcessamento
from avaliacao import Avaliacao
import export_results
import datetime
import math
from tqdm import tqdm

inicio = datetime.datetime.now()
database = postgis_database.Database()

missing_dataset = pd.read_csv('dataset/desaparecidos_MG.csv', header=0, encoding='latin-1')
g = graph.Graph('dataset/profiles_MG.csv')
pre_processamento = PreProcessamento(database, g, missing_dataset)

profile_limit = 2  # recomendable amount of missing people
raio = 20000  # radius profile selection

missing_index = pre_processamento.get_missing_index()
database.delete_all_raio_missing()

print('\n Check if rij will be created')
arr_profile = []
person_region = {}
raio_missing = {}
arr_profile_missing_area = {}
arr_network = {}

for index_j in tqdm(missing_index):
    person_region[index_j] = 1
    arr_profile_missing_area[index_j], raio_missing[index_j] = database.select_profile_raio(index_j, raio, person_region[index_j])

    arr_network[index_j] = database.select_network_profiles(arr_profile_missing_area[index_j])
    database.insert_raio_missing(index_j, raio_missing[index_j])

    for network_index_i in arr_network[index_j]:
        arr_profile.append(network_index_i)

database.delete_all_profile_not_in(arr_profile)


# for index_j in tqdm(missing_index):
#     missing = database.select_missing(index_j)
#     d_j = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='d[' + str(index_j) + ']')
#     expr_obj += d_j
#
#     arr_index_k = []
#     expr_R3 = LinExpr()
#
#     # arr_network = database.select_network_profiles(arr_profile_missing_area[index_j])
#
#     for network_index_k in arr_network[index_j]:
#         profile = database.select_profile(network_index_k)
#
#         d_k_j = m.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS,
#                          name='d[' + str(network_index_k) + '][' + str(index_j) + ']')
#
#         # expr_obj += d_k_j
#
#         expr_R3 += database.select_distance(missing['latitude'], missing['longitude'], profile['latitude'],
#                                             profile['longitude']) * d_k_j
#         expr_R4 = LinExpr()
#         mult = 1
#         for index_i in var_r:
#             try:
#                 mult *= database.select_influences(index_i, network_index_k)
#             except:
#                 pass
# 	    expr_R4 = mult * m.getVarByName('r[' + str(index_i) + '][' + str(index_j) + ']')
#         m.addConstr(expr_R4 >= d_k_j, 'R4_j' + str(index_j) + '_k' + str(network_index_k))
#     m.addConstr(expr_R3 == d_j, 'R3_j' + str(index_j))
#
#     expr_R1 = LinExpr()
#     soma_rij = 0
#     for r_index_i in var_r:
#         if len(var_r[r_index_i]) > 0:
#             try:
#                 r_i_j = m.getVarByName('r[' + str(r_index_i) + '][' + str(index_j) + ']')
#                 soma_rij += r_i_j
#                 expr_R1 += r_i_j
#             except:
#                 pass
#     # expr_obj += soma_rij
#     m.addConstr(expr_R1 <= 1, 'R1_j' + str(index_j))







