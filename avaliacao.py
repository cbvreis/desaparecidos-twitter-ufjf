#!/usr/bin/python
# -*- coding: utf-8 -*-
import postgis_database
from tqdm import tqdm
import datetime
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.mlab as mlab


class Avaliacao:

    def __init__(self, database):
        self.database = database
        self.perfis_area_desaparecido = {}
        self.desaparecidos = {}
        self.all_desaparecidos = {}
        self.perfil = {}
        profiles = self.database.select_all_profile()
        self.perfil['total'] = len(profiles)
        self.all_desaparecidos = self.database.select_all_missing()
        self.desaparecidos['total_desaparecidos'] = len(self.all_desaparecidos)
        self.arr_distancias = {}

        self.maior_raio = int(self.database.select_larger_missing_raio())
        self.step = int(self.maior_raio / 5)
        print("\n MAIOR RAIO " + str(self.maior_raio))
        print("\n STEP: " + str(self.step))

    def influenciados_raio(self):
        arr_perfis_r1 = []
        arr_perfis_r2 = []
        arr_perfis_r3 = []

        arr_perfis_influenciados_r1 = []
        arr_perfis_influenciados_r2 = []
        arr_perfis_influenciados_r3 = []

        arr_influenciados = []
        arr_influenciados_area = []

        desaparecido_influenciado = 0
        for index_j in tqdm(self.all_desaparecidos):
            dj = self.database.select_result_dj(index_j)
            if dj > 0:
                desaparecido_influenciado += 1

            raio = self.database.select_raio_missing(index_j)
            perfis_r1 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                     self.all_desaparecidos[index_j]['longitude'], (raio * 0.3))
            perfis_r2 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                     self.all_desaparecidos[index_j]['longitude'], (raio * 0.6))
            perfis_r3 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                     self.all_desaparecidos[index_j]['longitude'], raio)

            for r1 in perfis_r1:
                if r1 not in arr_perfis_r1:
                    arr_perfis_r1.append(r1)

            for r2 in perfis_r2:
                if r2 not in arr_perfis_r2:
                    arr_perfis_r2.append(r2)

            for r3 in perfis_r3:
                if r3 not in arr_perfis_r3:
                    arr_perfis_r3.append(r3)

            influenciados_r1 = influenciados_r2 = influenciados_r3 = 0
            total_perfis_influenciados = 0
            total_influenciados_area = 0
            total_influenciados_fora_area = 0
            arr_d_kj = self.database.select_result_dkj_by_missing(index_j)
            for index_k in arr_d_kj:
                if arr_d_kj[index_k][index_j] > 0:
                    total_perfis_influenciados += 1
                    if index_k not in arr_influenciados:
                        arr_influenciados.append(index_k)

                    if (index_k in perfis_r1) or (index_k in perfis_r2) or (index_k in perfis_r3):
                        if index_k not in arr_influenciados_area:
                            arr_influenciados_area.append(index_k)
                        total_influenciados_area += 1
                    else:
                        total_influenciados_fora_area += 1

                    if index_k in perfis_r1:
                        influenciados_r1 += 1
                        if index_k not in arr_perfis_influenciados_r1:
                            arr_perfis_influenciados_r1.append(index_k)

                    if index_k in perfis_r2:
                        influenciados_r2 += 1
                        if index_k not in arr_perfis_influenciados_r2:
                            arr_perfis_influenciados_r2.append(index_k)

                    if index_k in perfis_r3:
                        influenciados_r3 += 1
                        if index_k not in arr_perfis_influenciados_r3:
                            arr_perfis_influenciados_r3.append(index_k)

            # print("\n<---Desaparecido " + str(index_j) + "---->")
            #
            # print("total_perfis: " + str(len(perfis_r3)))
            # print("total_perfis_influenciados: " + str(total_perfis_influenciados))
            # print("total_influenciados_area: " + str(total_influenciados_area))
            # print("total_influenciados_fora_area: " + str(total_influenciados_fora_area))
            #
            # print("total_perfis_r1: " + str(len(perfis_r1)))
            # print("total_perfis_r2: " + str(len(perfis_r2)))
            # print("total_perfis_r3: " + str(len(perfis_r3)))
            # print("influenciados_r1: " + str(influenciados_r1))
            # print("influenciados_r2: " + str(influenciados_r2))
            # print("influenciados_r3: " + str(influenciados_r3))
            # print("\n")
            #
            # # informações para o grafico distancia x perfis
            # for raio in range(0, self.maior_raio + self.step, self.step):
            #     desparecido = self.all_desaparecidos[index_j]
            #     arr_profile = self.database.select_dwithin(desparecido['latitude'],
            #                                                desparecido['longitude'], raio)
            #
            #     perfis_raio = len(arr_profile)
            #     # influenciados_raio += self.database.select_influenced_profiles_by_missing_raio(index_j, raio)
            #     influenciados_raio = 0
            #     for index_k in arr_profile:
            #         d_kj = self.database.select_result_dkj(index_k, index_j)
            #         if d_kj > 0:
            #             influenciados_raio += 1
            #     try:
            #         self.arr_distancias[raio]["total"] += perfis_raio
            #     except:
            #         self.arr_distancias[raio] = {}
            #         self.arr_distancias[raio]["total"] = 0
            #         self.arr_distancias[raio]["total"] += perfis_raio
            #
            #     try:
            #         self.arr_distancias[raio]["influenciados"] += influenciados_raio
            #     except:
            #         self.arr_distancias[raio]["influenciados"] = 0
            #         self.arr_distancias[raio]["influenciados"] += influenciados_raio

            self.perfis_area_desaparecido[index_j] = {
                'total_perfis': len(perfis_r3),
                'total_perfis_influenciados': total_perfis_influenciados,
                'total_influenciados_area': total_influenciados_area,
                'total_influenciados_fora_area': total_influenciados_fora_area,
                'total_perfis_r1': len(perfis_r1),
                'total_perfis_r2': len(perfis_r2),
                'total_perfis_r3': len(perfis_r3),
                'influenciados_r1': influenciados_r1,
                'influenciados_r2': influenciados_r2,
                'influenciados_r3': influenciados_r3,
                'influenciador_r1_porc': 0,
                'influenciador_r2_porc': 0,
                'influenciador_r3_porc': 0
            }

            if self.perfis_area_desaparecido[index_j]['total_perfis_r1'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r1_porc'] = (influenciados_r1 * 100) / len(
                    perfis_r1)
            if self.perfis_area_desaparecido[index_j]['total_perfis_r2'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r2_porc'] = (influenciados_r2 * 100) / len(
                    perfis_r2)
            if self.perfis_area_desaparecido[index_j]['total_perfis_r3'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r3_porc'] = (influenciados_r3 * 100) / len(
                    perfis_r3)

        self.desaparecidos['influenciados'] = desaparecido_influenciado

        self.perfil['R1'] = len(arr_perfis_r1)
        self.perfil['R2'] = len(arr_perfis_r2)
        self.perfil['R3'] = len(arr_perfis_r3)
        self.perfil['influenciados'] = len(arr_influenciados)
        self.perfil['influenciados_area'] = len(arr_influenciados_area)
        self.perfil['influenciados_R1'] = len(arr_perfis_influenciados_r1)
        self.perfil['influenciados_R2'] = len(arr_perfis_influenciados_r2)
        self.perfil['influenciados_R3'] = len(arr_perfis_influenciados_r3)

        # print(self.desaparecidos)
        # print(self.perfil)
        print(self.arr_distancias)
        self.resumo_perfis_area_desaparecido()

    def influenciados_raio_banco(self):
        for index_j in tqdm(self.all_desaparecidos):
            # select profile raio
            raio = self.database.select_raio_missing(index_j)
            total_perfis_r1 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                           self.all_desaparecidos[index_j]['longitude'], (raio * 0.3))
            total_perfis_r2 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                           self.all_desaparecidos[index_j]['longitude'], (raio * 0.6))
            total_perfis_r3 = self.database.select_dwithin(self.all_desaparecidos[index_j]['latitude'],
                                                           self.all_desaparecidos[index_j]['longitude'], raio)

            # select dkj index_j
            total_perfis_influenciados = self.database.select_influenced_profiles_by_missing(index_j)

            # select dkj index_j  profile in select profile raio
            total_perfis_influenciados_r1 = self.database.select_influenced_profiles_by_missing_raio(index_j,
                                                                                                     (raio * 0.3))
            total_perfis_influenciados_r2 = self.database.select_influenced_profiles_by_missing_raio(index_j,
                                                                                                     (raio * 0.6))
            total_perfis_influenciados_r3 = self.database.select_influenced_profiles_by_missing_raio(index_j, raio)

            print("<---Desaparecido " + str(index_j) + "---->")

            print("total_perfis: " + str(len(total_perfis_r3)))
            print("total_perfis_influenciados: " + str(total_perfis_influenciados))
            print("total_influenciados_area: " + str(total_perfis_influenciados_r3))
            print("total_influenciados_fora_area: " + str((total_perfis_influenciados - total_perfis_influenciados_r3)))
            print("total_perfis_r1: " + str(len(total_perfis_r1)))
            print("total_perfis_r2: " + str(len(total_perfis_r2)))
            print("total_perfis_r3: " + str(len(total_perfis_r3)))
            print("influenciados_r1: " + str(total_perfis_influenciados_r1))
            print("influenciados_r2: " + str(total_perfis_influenciados_r2))
            print("influenciados_r3: " + str(total_perfis_influenciados_r3))
            print("\n")

            self.perfis_area_desaparecido[index_j] = {
                'total_perfis': len(total_perfis_r3),
                'total_perfis_influenciados': total_perfis_influenciados,
                'total_influenciados_area': total_perfis_influenciados_r3,
                'total_influenciados_fora_area': (total_perfis_influenciados - total_perfis_influenciados_r3),
                'total_perfis_r1': len(total_perfis_r1),
                'total_perfis_r2': len(total_perfis_r2),
                'total_perfis_r3': len(total_perfis_r3),
                'influenciados_r1': total_perfis_influenciados_r1,
                'influenciados_r2': total_perfis_influenciados_r2,
                'influenciados_r3': total_perfis_influenciados_r3,
                'influenciador_r1_porc': 0,
                'influenciador_r2_porc': 0,
                'influenciador_r3_porc': 0
            }

            if self.perfis_area_desaparecido[index_j]['total_perfis_r1'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r1_porc'] = (
                                                                                          total_perfis_influenciados_r1 * 100) / len(
                    total_perfis_r1)
            if self.perfis_area_desaparecido[index_j]['total_perfis_r2'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r2_porc'] = (
                                                                                          total_perfis_influenciados_r2 * 100) / len(
                    total_perfis_r2)
            if self.perfis_area_desaparecido[index_j]['total_perfis_r3'] > 0:
                self.perfis_area_desaparecido[index_j]['influenciador_r3_porc'] = (
                                                                                          total_perfis_influenciados_r3 * 100) / len(
                    total_perfis_r3)

    def check_porcentagem_area(self, step):
        # self.influenciados_raio_banco()
        arr_porcentagem_area = {}
        arr_porcentagem_area['R1'] = {}
        arr_porcentagem_area['R2'] = {}
        arr_porcentagem_area['R3'] = {}
        for i in range(step, 100 + step, step):
            arr_porcentagem_area['R1'][i] = 0
            arr_porcentagem_area['R2'][i] = 0
            arr_porcentagem_area['R3'][i] = 0

        total_r1 = 0
        total_r2 = 0
        total_r3 = 0
        for index_j in tqdm(self.perfis_area_desaparecido):
            # print(index_j)
            # print(self.perfis_area_desaparecido[index_j])
            # print('\n')
            for i in range(step, 100 + step, step):
                if i >= self.perfis_area_desaparecido[index_j]['influenciador_r1_porc'] > i - step and \
                        self.perfis_area_desaparecido[index_j][
                            'influenciador_r1_porc'] != 0:
                    arr_porcentagem_area['R1'][i] += 1
                    total_r1 += 1

                if i >= self.perfis_area_desaparecido[index_j]['influenciador_r2_porc'] > i - step and \
                        self.perfis_area_desaparecido[index_j][
                            'influenciador_r2_porc'] != 0:
                    arr_porcentagem_area['R2'][i] += 1
                    total_r2 += 1

                if i >= self.perfis_area_desaparecido[index_j]['influenciador_r3_porc'] > i - step and \
                        self.perfis_area_desaparecido[index_j][
                            'influenciador_r3_porc'] != 0:
                    # print(" i->"+str(i)+" por->"+str(self.perfis_area_desaparecido[index_j]['influenciador_r3_porc'])+"
                    # i-step->"+str((i - step)))
                    arr_porcentagem_area['R3'][i] += 1
                    total_r3 += 1

        print("total_r1=" + str(total_r1))
        print("total_r2=" + str(total_r2))
        print("total_r3=" + str(total_r3))

        return arr_porcentagem_area

    def graph_areas(self):
        step = 10
        arr_porcentagem_area = self.check_porcentagem_area(step)
        print(arr_porcentagem_area)
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')

        colors = []

        # Definimos los datos
        x3 = []  # inicio porcentagem
        y3 = []
        width = []  # percentual atingido
        top = []  # quant de desaparecidos
        for i in range(0, 100, step):  # R1
            colors.append('blue')
            x3.append(i)
            y3.append(0)
            width.append(step)
            top.append(arr_porcentagem_area['R1'][i + step])

        for i in range(0, 100, step):  # R2
            colors.append('red')
            x3.append(i)
            y3.append(1)
            width.append(step)
            top.append(arr_porcentagem_area['R2'][i + step])

        for i in range(0, 100, step):  # R3
            colors.append('green')
            x3.append(i)
            y3.append(2)
            width.append(step)
            top.append(arr_porcentagem_area['R3'][i + step])

        z3 = np.zeros(3 * (100 / step))
        depth = np.ones(3 * (100 / step))

        # utilizamos el método bar3d para graficar las barras
        ax1.bar3d(x3, y3, z3, width, depth, top, color=colors)

        # title
        # ax1.set_title('Grafico 3d')
        ax1.set_xlabel('porcentagem atingida')
        # ax1.set_ylabel('R1 R2 R3')
        # plt.yticks('', [])
        ax1.set_zlabel('quantidade de desaparecidos')

        # ax1.legend(['blue', 'red', 'green'], ['R1', 'R2','R3'])
        blue_proxy = plt.Rectangle((0, 0), 1, 1, fc="b")
        red_proxy = plt.Rectangle((0, 0), 1, 1, fc="r")
        green_proxy = plt.Rectangle((0, 0), 1, 1, fc="green")
        ax1.legend([blue_proxy, red_proxy, green_proxy], ['R1', 'R2', 'R3'], loc='upper left')
        # Mostramos el gráfico
        plt.show()

    def histograma_desaparecidos(self):
        #
        # # plt.hist(x,bins=10)
        #
        # first_edge, last_edge = min(x), max(x)
        #
        # n_equal_bins = 20  # NumPy's default
        # bin_edges = np.linspace(start=first_edge, stop=last_edge, num=n_equal_bins + 1, endpoint=True)
        #
        # plt.hist(x, bins=bin_edges)
        # plt.ylabel('Desaparecidos')
        # plt.xlabel('Informacao dispersa sobre cada desaparecido')
        x = self.database.select_all_value_result_dj()
        print(" ******** X **********")
        print(x)
        plt.hist(x, bins=50)
        plt.ylabel('Desaparecidos')
        plt.xlabel('Informacao dispersa sobre cada desaparecido')
        plt.show()

    def energia_profile(self):
        x = []
        y = []
        porc_inf_R3 = []  # % desaparecidos influenciados em R3
        arr_dj = []  # dj
        for index_j in self.database.select_all_missing():
            desaparecido = self.database.select_missing(index_j)
            if desaparecido['longitude'] != -38.9646608 and desaparecido['latitude'] != -12.259727:
                x.append(desaparecido['longitude'])
                y.append(desaparecido['latitude'])
                porc_inf_R3.append(self.perfis_area_desaparecido[index_j]['influenciador_r3_porc'])
                arr_dj.append((self.database.select_result_dj(index_j) / 30))

        plt.scatter(x, y, c=porc_inf_R3, cmap='viridis', s=arr_dj)
        plt.colorbar()
        plt.ylabel('Latitude')
        plt.xlabel('Longitude')
        # plt.title("Porcentagem de perfis cobertos por desaparecido")
        plt.show()

    def perfis_area_pizza(self):
        print("Creating graph ...")
        influenciados_area = self.perfil['influenciados_area']
        influenciados_fora_area = self.perfil['influenciados'] - self.perfil['influenciados_area']

        labels = 'Fora da area', 'Dentro da area'
        sizes = [influenciados_fora_area, influenciados_area]
        colors = ['gold', 'lightskyblue']
        explode = (0.1, 0,)  # explode 1st slice

        # Plot
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140)

        plt.axis('equal')
        # plt.title("Perfis Influenciados")
        plt.show()

    def print_graph_by_desaparecido(self, index_j):
        print('Creating .graph results...')

        desaparecido = self.database.select_missing(index_j)
        tabela_label = []

        x_desaparecido = desaparecido['longitude']
        y_desaparecido = desaparecido['latitude']
        x_perfil_influenciador = []
        y_perfil_influenciador = []
        x_perfil_influenciado = []
        y_perfil_influenciado = []
        x_perfil_nao_influenciador = []
        y_perfil_nao_influenciador = []
        tabela_label.append({'label': index_j,
                             'x': desaparecido['longitude'],
                             'y': desaparecido['latitude']})

        for index_i in self.database.select_all_profile():
            profile = self.database.select_profile(index_i)
            tabela_label.append(
                {'label': index_i, 'x': profile['longitude'], 'y': profile['latitude']})

            r_ij = self.database.select_result_r(index_i, index_j)
            d_kj = self.database.select_result_dkj(index_i, index_j)
            if r_ij == 1.0:
                x_perfil_influenciador.append(profile['longitude'])
                y_perfil_influenciador.append(profile['latitude'])

            elif d_kj > 0.00001:
                x_perfil_influenciado.append(profile['longitude'])
                y_perfil_influenciado.append(profile['latitude'])

            else:
                x_perfil_nao_influenciador.append(profile['longitude'])
                y_perfil_nao_influenciador.append(profile['latitude'])

        # dados
        desaparecido = ([x_desaparecido], [y_desaparecido])
        perfil_influenciadores = (x_perfil_influenciador, y_perfil_influenciador)
        perfil_influenciado = (x_perfil_influenciado, y_perfil_influenciado)
        perfil = (x_perfil_nao_influenciador, y_perfil_nao_influenciador)

        # agrupa tabela
        tabela_completa = (desaparecido, perfil_influenciadores, perfil_influenciado, perfil)

        # determina cor de cada estado no grafico
        cores = ("blue", "red", "green")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil_Influenciador", "Perfil_Influenciado")

        # Create plot
        plt.figure()

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        for i, data in enumerate(tabela_label):
            plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'],
                     fontsize=9)

        # titulo do grafico
        plt.title('Grafico Desaparecido ' + str(index_j))

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('resultados/desaparecido_' + str(index_j) + '_influenciador_influenciados.pdf')
        plt.show()
        print('Done!')

    def print_graph_perfis_Desaparecidos(self):
        print('Creating .graph results...')

        tabela_label = []
        x_perfil = []
        y_perfil = []
        for index_i in self.database.select_all_profile():
            profile = self.database.select_profile(index_i)
            tabela_label.append(
                {'label': index_i, 'x': profile['longitude'], 'y': profile['latitude']})

            x_perfil.append(profile['longitude'])
            y_perfil.append(profile['latitude'])

        x_desaparecido = []
        y_desaparecido = []
        for index_j in self.database.select_all_missing():
            desaparecido = self.database.select_missing(index_j)
            x_desaparecido.append(desaparecido['longitude'])
            y_desaparecido.append(desaparecido['latitude'])

        # dados
        desaparecido = ([x_desaparecido], [y_desaparecido])
        perfil = (x_perfil, y_perfil)

        # agrupa tabela
        tabela_completa = (desaparecido, perfil)

        # determina cor de cada estado no grafico
        cores = ("blue", "red")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil")

        # Create plot
        plt.figure()

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        # for i, data in enumerate(tabela_label):
        #     plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'],
        #              fontsize=9)

        # titulo do grafico
        # plt.title('Grafico Desaparecido e Perfis ')

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.show()
        print('Done!')

    def distancia_desaparecido(self):
        print("Creating graph distancia_desaparecido ...")
        yBar = []
        xLabel = []
        z = []
        for raio in self.arr_distancias:
            yBar.append(self.arr_distancias[raio]["total"])
            z.append(self.arr_distancias[raio]["influenciados"])
            xLabel.append(raio)

        xBar = range(len(yBar))
        plt.bar(xBar, yBar, color='blue', align='center')
        plt.plot(xBar, z, color='black', marker='o', linestyle='-', linewidth=2)
        plt.show()
        print('Done!')

    def influenciados_by_desaparecido(self):

        # Values of each group
        n_influenciados = []
        influenciados = []
        label_x = []
        for index_j in self.perfis_area_desaparecido:
            total_perfis = self.perfis_area_desaparecido[index_j]['total_perfis']
            total_influenciados = self.perfis_area_desaparecido[index_j]['total_influenciados_area']

            n_influenciados.append((total_perfis - total_influenciados))
            influenciados.append(total_influenciados)
            label_x.append(index_j)

        # The position of the bars on the x-axis
        influenciados.sort()
        n_influenciados.sort()
        index_x = range(len(self.perfis_area_desaparecido))

        barWidth = 1

        # Create brown bars
        plt.bar(index_x, influenciados, color='blue', edgecolor='white', width=barWidth)

        # Create green bars (middle), on top of the firs ones
        plt.bar(index_x, n_influenciados, bottom=influenciados, color='green', edgecolor='white', width=barWidth)

        # Custom X axis
        plt.xticks(index_x, label_x, fontweight='bold')
        plt.xlabel("group")

        # Show graphic
        Blue_patch = mpatches.Patch(color='blue', label='Perfis infuenciados')
        Green_path = mpatches.Patch(color='green', label='Perfis nao infuenciados')
        plt.legend(handles=[Blue_patch, Green_path])
        plt.show()

    def exemplo_N(self):
        print('Creating .graph results...')

        x_perfil = [-43.9, -43.6, -43.6]
        y_perfil = [-19.9, -19.9, -19.6]
        x_desaparecido = [-43.8, -43.9, -43.7, -43.6]
        y_desaparecido = [-19.7, -19.7, -19.7, -19.7]
        tabela_label = {
            0: {"label": "d1", "x": -43.8, "y": -19.7},
            1: {"label": "d2", "x": -43.9, "y": -19.7},
            2: {"label": "d3", "x": -43.7, "y": -19.7},
            3: {"label": "d4", "x": -43.6, "y": -19.7},
            4: {"label": "p1", "x": -43.9, "y": -19.9},
            5: {"label": "p2", "x": -43.6, "y": -19.9},
            6: {"label": "p3", "x": -43.6, "y": -19.6}
        }
        # dados
        desaparecido = ([x_desaparecido], [y_desaparecido])
        perfil = (x_perfil, y_perfil)

        # agrupa tabela
        tabela_completa = (desaparecido, perfil)

        # determina cor de cada estado no grafico
        cores = ("blue", "red")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil")

        # Create plot
        plt.figure()

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        for i, data in enumerate(tabela_label):
            plt.text(tabela_label[i]['x'] - 0.001, tabela_label[i]['y'] - 0.001, tabela_label[i]['label'],
                     fontsize=9)

        plt.title('Grafico Desaparecido e Perfis ')

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.show()
        print('Done!')

    def resumo_perfis_area_desaparecido(self):
        print('Resumo ...')
        print(self.desaparecidos)
        total_perfil_r1 = self.perfil['R1']
        total_perfil_r2 = self.perfil['R2']
        total_perfil_r3 = self.perfil['R3']

        total_perfis_area_desaparecido = self.perfil['R3']

        total_perfis_influenciados = self.perfil['influenciados']
        influenciados_r1 = self.perfil['influenciados_R1']
        influenciados_r2 = self.perfil['influenciados_R2']
        influenciados_r3 = self.perfil['influenciados_R3']

        influenciados_area = self.perfil['influenciados_area']
        influenciados_fora_area = self.perfil['influenciados'] - self.perfil['influenciados_area']

        print("-------- RESULTADO ABSOLUTO ---------")

        print("Total de Perfis: " + str(self.perfil['total']))
        print("Total de Perfis Dentro da area: " + str(total_perfis_area_desaparecido))
        print("Total de Perfis influenciados: " + str(total_perfis_influenciados))
        print("Total de Perfis influenciados dentro da area: " + str(influenciados_area))
        print("Total de Perfis influenciados fora da area: " + str(influenciados_fora_area))
        print("Total de Perfis em R1: " + str(total_perfil_r1) + " - Total de Perfis influenciados R1: " + str(
            influenciados_r1))
        print("Total de Perfis em R2: " + str(total_perfil_r2) + " - Total de Perfis influenciados R2: " + str(
            influenciados_r2))
        print("Total de Perfis em R3: " + str(total_perfil_r3) + " - Total de Perfis influenciados R3: " + str(
            influenciados_r3))

        print('\n')

        print("-------- RESULTADO PORCENTAGEM EM RELACAO AOS PERFIS INFLUENCIADOS ---------")
        print("Perfis influenciados dentro da area: " + str(
            (influenciados_area * 100) / total_perfis_influenciados) + "%")
        print("Perfis influenciados fora da area: " + str(
            (influenciados_fora_area * 100) / total_perfis_influenciados) + "%")
        print("Perfis influenciados R1: " + str((influenciados_r1 * 100) / total_perfis_influenciados) + "%")
        print("Perfis influenciados R2: " + str((influenciados_r2 * 100) / total_perfis_influenciados) + "%")
        print("Perfis influenciados R3: " + str((influenciados_r3 * 100) / total_perfis_influenciados) + "%")

        print('\n')

        print("-------- RESULTADO PORCENTAGEM EM RELACAO AOS PERFIS DENTRO DA AREA R* ---------")
        print("Perfis influenciados dentro da area: " + str(
            (influenciados_area * 100) / total_perfis_area_desaparecido) + "%")
        print("Perfis influenciados R1: " + str((influenciados_r1 * 100) / total_perfil_r1) + "%")
        print("Perfis influenciados R2: " + str((influenciados_r2 * 100) / total_perfil_r2) + "%")
        print("Perfis influenciados R3: " + str((influenciados_r3 * 100) / total_perfil_r3) + "%")

        print('\n')

        # self.print_graph_by_desaparecido(4)


inicio = datetime.datetime.now()

database = postgis_database.Database()
avaliacao = Avaliacao(database)
avaliacao.influenciados_raio()
# avaliacao.graph_areas()
# avaliacao.energia_profile()
avaliacao.histograma_desaparecidos()
# avaliacao.perfis_area_pizza()
# avaliacao.distancia_desaparecido()
# avaliacao.influenciados_by_desaparecido()
# avaliacao.print_graph_perfis_Desaparecidos()
# avaliacao.print_graph_by_desaparecido(30)
# avaliacao.exemplo_N()

fim = datetime.datetime.now()
print('TEMPO DE EXECUÇÃO: ' + str(fim - inicio))
