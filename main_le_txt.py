#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from tqdm import tqdm
from gurobipy import *
import postgis_database

inicio = datetime.datetime.now()
database = postgis_database.Database()
# Model Start
m = Model('missing_txt')

profile_limit = 2  # recomendable amount of missing people
var_r = {}
# Model Start
m = Model('missing')

print("Creating Obj ...")
arq_Obj = open("file_txt/Obj.txt", "r")
expr_obj = LinExpr()
inicio_Obj = datetime.datetime.now()
for linha in arq_Obj:
    linha_expr = linha.replace(']', '-').replace('[', '-').split('-')
    index_j = linha_expr[1]
    d_j = m.addVar(lb=0.0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name='d[' + str(int(index_j)) + ']')
    expr_obj += d_j
m.setObjective(expr_obj, GRB.MAXIMIZE)
arq_Obj.close()
fim_Obj = datetime.datetime.now()
print("TEMPO DE EXECUÇÂO Obj: " + str((fim_Obj - inicio_Obj)))

m.update()

print("Creating R2 ...")
arq_R2 = open("file_txt/R2.txt", "r")
flag = 0
expr_R2 = LinExpr()
inicio_R2 = datetime.datetime.now()
for linha in tqdm(arq_R2):
    linha_R = linha.split(' ')
    linha_r = linha.replace(']', '-').replace('[', '-').split('-')
    if len(linha_R) > 1:
        if flag:
            m.addConstr(expr_R2 <= profile_limit, 'R2_i' + str(int(index_i)))
            index_i = linha_R[1]
        else:
            index_i = linha_R[1]
        expr_R2 = LinExpr()
    if linha_r[0] == 'r':
        expr_R2 += m.addVar(vtype=GRB.BINARY, name='r[' + str(int(linha_r[1])) + '][' + str(int(linha_r[3])) + ']')
    flag += 1
m.addConstr(expr_R2 <= profile_limit, 'R2_i' + str(index_i))
arq_R2.close()
fim_R2 = datetime.datetime.now()
print("TEMPO DE EXECUÇÂO R2: " + str((fim_R2 - inicio_R2)))

m.update()

print("Creating R1 ...")
arq_R1 = open("file_txt/R1.txt", "r")
flag = 0
inicio_R1 = datetime.datetime.now()
expr_R1 = LinExpr()
for linha in tqdm(arq_R1):
    linha_R = linha.split(' ')
    linha_r = linha.replace(']', '-').replace('[', '-').split('-')
    if len(linha_R) > 1:
        if flag:
            m.addConstr(expr_R1 <= 1, 'R1_j' + str(int(index_j)))
            index_j = linha_R[1]
        else:
            index_j = linha_R[1]
        expr_R1 = LinExpr()
    if linha_r[0] == 'r':
        try:
            var_r[linha_r[1]].append(linha_r[3])
        except:
            var_r[linha_r[1]] = []
            var_r[linha_r[1]].append(linha_r[3])
        try:
            expr_R1 += m.getVarByName('r[' + str(int(linha_r[1])) + '][' + str(int(linha_r[3])) + ']')
        except:
            pass
    flag += 1
m.addConstr(expr_R1 <= 1, 'R1_j' + str(int(index_j)))
arq_R1.close()
fim_R1 = datetime.datetime.now()
print("TEMPO DE EXECUÇÂO R1: " + str((fim_R1 - inicio_R1)))

m.update()

print("Creating R3 ...")
arq_R3 = open("file_txt/R3.txt", "r")
flag = 0
expr_R3 = LinExpr()
inicio_R3 = datetime.datetime.now()
for linha in arq_R3:
    linha_R = linha.split(' ')
    if len(linha_R) == 2:
        if flag:
            d_j = m.getVarByName('d[' + str(int(index_j)) + ']')
            m.addConstr(expr_R3 == d_j, 'R3_j' + str(index_j))
            index_j = int(linha_R[1])
        else:
            index_j = int(linha_R[1])
        expr_R3 = LinExpr()

    else:
        linha_expr = linha_R[2].replace(']', '-').replace('[', '-').split('-')
        d_kj = m.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS,
                        name='d[' + str(int(linha_expr[1])) + '][' + str(int(linha_expr[3])) + ']')
        g_kj = linha_R[0]
        expr_R3 += g_kj * d_kj
    flag += 1
d_j = m.getVarByName('d[' + str(int(index_j)) + ']')
m.addConstr(expr_R3 == d_j, 'R3_j' + str(index_j))
arq_R3.close()
fim_R3 = datetime.datetime.now()
print("TEMPO DE EXECUÇÂO R3: " + str((fim_R3 - inicio_R3)))

m.update()

print("Creating R4 ...")
arq_R4 = open("file_txt/R4.txt", "r")
flag = 0
expr_R4 = LinExpr()
inicio_R4 = datetime.datetime.now()
for linha in arq_R4:
    linha_R = linha.split(' ')
    if len(linha_R) == 4:
        if flag:
            d_k_j = m.getVarByName('d[' + str(int(index_k)) + '][' + str(int(index_j)) + ']')
            m.addConstr(expr_R4 >= d_k_j, 'R4_j' + str(index_j) + '_k' + str(index_k))
            index_j = linha_R[1]
            index_k = linha_R[3]
        else:
            index_j = linha_R[1]
            index_k = linha_R[3]
        expr_R4 = LinExpr()
    else:
        linha_expr = linha_R[2].replace(']', '-').replace('[', '-').split('-')
        try:
            r_ij = m.getVarByName('r[' + str(int(linha_expr[1])) + '][' + str(int(linha_expr[3])) + ']')
            f_ik = linha_R[0]
            expr_R4 += f_ik * r_ij
        except:
            pass
    flag += 1
d_k_j = m.getVarByName('d[' + str(int(index_k)) + '][' + str(int(index_j)) + ']')
m.addConstr(expr_R4 >= d_k_j, 'R4_j' + str(index_j) + '_k' + str(index_k))
arq_R4.close()

fim_R4 = datetime.datetime.now()
print("TEMPO DE EXECUÇÂO R4: " + str((fim_R4 - inicio_R4)))

m.update()

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
m.write('resultados/model_txt.lp')
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

print('\n Close database connection...')
database.close_connection()
