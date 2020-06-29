# -*- coding: utf-8 -*-
import postgis_database
import csv
import matplotlib.pyplot as plt


class Analise:

    def __init__(self, database):
        print('Creating Analise...')
        self.database = database
        self.desaparecidos = {}
        self.perfis = {}
        self.analise_desaparecidos = {}
        self.r_ij = {}
        self.d_kj = {}
        self.arr_j_sem_influenciadores = []
        self.arr_j_com_influenciadores = []
        self.arr_perfis_area = []
        self.arr_perfis_influenciados = []
        self.arr_perfis_influenciadores = []
        self.total_desaparecidos_msm_ponto = 0

        self.read_file()
        self.select_in_raio()
        self.get_estatistica_desaparecidos_msm_ponto()
        self.conclusao()
        # self.print_graph_perfis()
        # self.print_graph_all_desaparecidos()
        # self.print_graph_desaparecidos()
        #self.print_graph_arr_j_sem_influenciadores()
        # self.print_graph_by_desaparecido()
        #self.print_graph_arr_j_com_influenciadores()

    def read_file(self):
        print('Reading file...')
        index_perfis = []
        file = open("resultados/resultado.txt", "r+")
        # file = open("teste_leitura.txt","r+")

        for line in file:

            line = line.replace(']', '-').replace('[', '-').replace(':', '-').split('-')
            try:
                while '' in line:
                    line.remove('')
            except:
                pass

            if line[0] != 'r' and line[0] != 'd':
                continue

            # r_ij
            if line[0] == 'r':
                self.get_val_r(line, index_perfis)
            # d_k_j
            if line[0] == 'd' and len(line) > 3:
                self.get_val_d(line, index_perfis)

        print('total de Perfis: ' + str(len(self.perfis)))
        print('total de Desaparecidos: ' + str(len(self.desaparecidos)))
        print('Done!')

    def get_val_r(self, line, index_perfis):
        index_p = int(line[1])
        index_j = int(line[2])
        line[3] = line[3].replace('\n', '')
        value = float(line[3])

        try:
            self.desaparecidos[index_j]
        except:
            self.desaparecidos[index_j] = {'p_influenciados': [], 'p_area': [], 'd_area': [], 'raio': 2000,
                                           'lat': '', 'lon': ''}

        if index_p not in index_perfis:
            self.perfis[index_p] = 0
            index_perfis.append(index_p)

        try:
            self.r_ij[index_p][index_j] = value
        except:
            self.r_ij[index_p] = {}
            self.r_ij[index_p][index_j] = value

        if self.r_ij[index_p][index_j] > 0:
            self.desaparecidos[index_j]['p_influenciados'].append(index_p)
            self.perfis[index_p] += 1
            if index_p not in self.arr_perfis_influenciadores:
                self.arr_perfis_influenciadores.append(index_p)

    def get_val_d(self, line, index_perfis):
        index_p = int(line[1])
        index_j = int(line[2])
        line[3] = line[3].replace('\n', '')
        value = float(line[3])


        if index_p not in index_perfis:
            self.perfis[index_p] = 0
            index_perfis.append(index_p)

        try:
            self.d_kj[index_p][index_j] = value
        except:
            self.d_kj[index_p] = {}
            self.d_kj[index_p][index_j] = value

        if self.d_kj[index_p][index_j] > 0:
            self.desaparecidos[index_j]['p_influenciados'].append(index_p)

            if index_p not in self.arr_perfis_influenciados:
                self.arr_perfis_influenciados.append(index_p)

    def select_in_raio(self):
        print('select_in_raio...')
        raio = 20000
        person_region = 1

        for index_j in self.desaparecidos:
            missing = self.database.select_missing(index_j)
            if missing:
                perfis_area, new_raio = self.database.select_profile_raio(index_j, raio, person_region)
                desaparecidos_area = database.select_missing_raio(index_j, new_raio)
                self.desaparecidos[index_j]['p_area'] = perfis_area
                self.desaparecidos[index_j]['raio'] = new_raio
                self.desaparecidos[index_j]['d_area'] = desaparecidos_area
                self.desaparecidos[index_j]['lat'] = missing['latitude']
                self.desaparecidos[index_j]['lon'] = missing['longitude']

                if len(self.desaparecidos[index_j]['p_influenciados']) == 0:
                    self.arr_j_sem_influenciadores.append(index_j)
                else:
                    self.arr_j_com_influenciadores.append(index_j)

        print('Done!')

    def conclusao(self):
        print('conclusao...')

        print("Total de Desaparecidos: " + str(len(self.desaparecidos)))
        print("Total de Desaparecidos com influenciadores: " + str(len(self.arr_j_com_influenciadores)))
        print("Total de Desaparecidos sem influenciadores: " + str(len(self.arr_j_sem_influenciadores)))

        print("Total de Perfis: " + str(len(self.perfis)))
        print("Total de Perfis influenciadores: " + str(len(self.arr_perfis_influenciadores)))
        print("Total de Perfis que recebem informação de algum desaparecido: "
              + str(len(self.arr_perfis_influenciados)))

        print("Total de Perfis não atingidos: "
              + str((len(self.perfis) - len(self.arr_perfis_influenciadores)))
              )

        print('Done!')

    def get_estatistica_desaparecidos_msm_ponto(self, print_bool = False):
        print("\n Desaparecidos no msm ponto")

        total_desaparecidos_msm_ponto = {}

        for index_j in self.desaparecidos:
            x = self.desaparecidos[index_j]['lon']
            y = self.desaparecidos[index_j]['lat']

            arr_desaparecidos_area = self.database.select_missing_by_lon_lat(x, y)
            raio = self.desaparecidos[arr_desaparecidos_area[0]]['raio']

            desaparecidos_msm_ponto = self.database.select_missing_raio(arr_desaparecidos_area[0], 0)
            desaparecidos_area = self.database.select_missing_raio(arr_desaparecidos_area[0], raio)
            arr_perfis = self.database.select_dwithin(y, x, raio)

            try:
                total_desaparecidos_msm_ponto[x][y] += 1
            except:
                total_desaparecidos_msm_ponto[x] = {}
                total_desaparecidos_msm_ponto[x][y] = 1

            arr_influencer_area = []
            arr_influencer_fora = []
            arr_not_influencer = []
            for index_p in arr_perfis:
                if index_p not in self.arr_perfis_area:
                    self.arr_perfis_area.append(index_p)

                arr_desaparecidos_influenciados = self.get_desaparecidos_influenciados(index_p)
                if not arr_desaparecidos_influenciados:
                    arr_not_influencer.append(index_p)
                    continue

                if len(self.intersection(arr_desaparecidos_influenciados, arr_desaparecidos_area)) > 0:
                    arr_influencer_area.append(index_p)
                else:
                    arr_influencer_fora.append(index_p)

            if print_bool:
                print("\n ponto(" + str(x) + " " + str(y) + ")")
                print("\t total desaparecidos no ponto: " + str(len(desaparecidos_msm_ponto)))
                print("\t desaparecidos sem influenciadores: " + str(self.desaparecidos[x][y]))
                print("\t desaparecidos na area: " + str(len(desaparecidos_area)))
                print("\t total perfis area: " + str(len(arr_perfis)))
                print("\t total perfis q influenciam area: " + str(len(arr_influencer_area)))
                print("\t total perfis q influenciam fora area: " + str(len(arr_influencer_fora)))
                print("\n")

        for lon in total_desaparecidos_msm_ponto:
            for lat in total_desaparecidos_msm_ponto[lon]:
                if total_desaparecidos_msm_ponto[lon][lat] > 1:
                    self.total_desaparecidos_msm_ponto += total_desaparecidos_msm_ponto[lon][lat]


    # def plt_grafico_desaparecidos_area(self,desaparecidos_area,arr_influencer_area, arr_influencer_fora, arr_perfis):

    def get_desaparecidos_influenciados(self, index_p):
        try:
            self.r_ij[index_p]
        except:
            return []
        arr_desaparecidos_influenciados = []
        for index_j in self.r_ij[index_p]:
            if self.r_ij[index_p][index_j] == 1:
                arr_desaparecidos_influenciados.append(index_j)
        return arr_desaparecidos_influenciados

    def print_csv_desaparecidos_perfil(self, arr_desaparecidos, arr_perfil, name):
        print('Creating .csv results...')
        _csv = csv.writer(open("resultados_10000d_1000p/" + str(name) + ".csv", "wb"))

        for index_j in arr_desaparecidos:
            missing = self.database.select_missing(index_j)
            _csv.writerow(['index', 'name', 'latitude', 'longitude'])
            _csv.writerow([str(index_j), missing['name'], missing['latitude'], missing['longitude']])
            _csv.writerow(['Perfis na  area', str(len(self.desaparecidos[index_j]['p_area']))])

            for index_i in self.desaparecidos[index_j]['p_area']:
                profile = self.database.select_profile(index_i)
                _csv.writerow(['index', 'name', 'latitude', 'longitude'])
                _csv.writerow([str(index_i), profile['profile_name'], profile['latitude'], profile['longitude']])
        print('Done!')

    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    ## GRAFICOS
    def print_graph_all_desaparecidos(self):
        x_desaparecidos = []
        y_desaparecidos = []

        tabela_label = []
        all_missing = self.database.select_all_missing()
        for index_j in all_missing:
            longitude = all_missing[index_j]['longitude']
            latitude = all_missing[index_j]['latitude']
            x_desaparecidos.append(longitude)
            y_desaparecidos.append(latitude)

            tabela_label.append(
                {'label': all_missing[index_j]['name'], 'x': longitude, 'y': latitude})

        # agrupa tabela
        tabela_completa = ([x_desaparecidos], [y_desaparecidos])

        # determina cor de cada estado no grafico
        cores = ("blue")

        # cria um label para os grupos
        label = ("Desaparecidos")

        # Create plot
        plt.figure()
        # plt.axis((-75, -34, -34, 5))

        # for data, color, group in zip(tabela_completa, cores, label):
        #     print(data)
        #     x, y = data
        #     plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        plt.scatter(x_desaparecidos, y_desaparecidos, s=30, c='BLUE', alpha=0.8)

        # for i, data in enumerate(tabela_label):
        #     plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

        # titulo do grafico
        plt.title('Desaparecidos')

        # insere legenda dos estados
        # plt.legend(loc=0)
        plt.xlabel('longitude')
        plt.ylabel('latitude')
        plt.savefig('resultados/graficos_analise_desparecidos_sem_label.pdf')
        plt.show()

    def print_graph_desaparecidos(self):
        x_desaparecidos_com_influencer = []
        y_desaparecidos_com_influencer = []

        x_desaparecidos_sem_influencer = []
        y_desaparecidos_sem_influencer = []

        tabela_label = []

        for index_j in self.desaparecidos:
            missing = self.database.select_missing(index_j)
            longitude = self.desaparecidos[index_j]['lon']
            latitude = self.desaparecidos[index_j]['lat']
            if index_j in self.arr_j_sem_influenciadores > 0:
                x_desaparecidos_sem_influencer.append(longitude)
                y_desaparecidos_sem_influencer.append(latitude)
            else:
                x_desaparecidos_com_influencer.append(longitude)
                y_desaparecidos_com_influencer.append(latitude)

            tabela_label.append(
                {'label': missing['name'], 'x': longitude, 'y': latitude})

        influencer = (x_desaparecidos_com_influencer, y_desaparecidos_com_influencer)
        not_influencer = (x_desaparecidos_sem_influencer, y_desaparecidos_sem_influencer)

        # agrupa tabela
        tabela_completa = (influencer, not_influencer)

        # determina cor de cada estado no grafico
        cores = ("blue", "gray")

        # cria um label para os grupos
        label = ("Desaparecidos com influenciadores", "Desaparecidos sem influenciadores")

        # Create plot
        plt.figure()
        # plt.axis((-75, -34, -34, 5))

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        # for i, data in enumerate(tabela_label):
        #     plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

        # titulo do grafico
        plt.title('Desaparecidos')

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('resultados/graficos_analise_desparecidos_sem_label.pdf')
        plt.show()

    def print_graph_perfis(self):
        x_perfil_influencer = []
        y_perfil_influencer = []

        x_perfil_not_influencer = []
        y_perfil_not_influencer = []

        tabela_label = []

        for index_p in self.perfis:
            profile = self.database.select_profile(index_p)
            if self.perfis[index_p] > 0:
                x_perfil_influencer.append(profile['longitude'])
                y_perfil_influencer.append(profile['latitude'])
            else:
                x_perfil_not_influencer.append(profile['longitude'])
                y_perfil_not_influencer.append(profile['latitude'])

            tabela_label.append(
                {'label': profile['profile_name'], 'x': profile['longitude'], 'y': profile['latitude']})

        influencer = (x_perfil_influencer, y_perfil_influencer)
        not_influencer = (x_perfil_not_influencer, y_perfil_not_influencer)

        # agrupa tabela
        tabela_completa = (influencer, not_influencer)

        # determina cor de cada estado no grafico
        cores = ("blue", "gray")

        # cria um label para os grupos
        label = ("Influenciadores", "Perfil")

        # Create plot
        plt.figure()
        # plt.axis((-75, -34, -34, 5))

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        for i, data in enumerate(tabela_label):
            plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

        # titulo do grafico
        plt.title('Perfis')

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('resultados/graficos_analise_perfis_sem_label.pdf')
        plt.show()

    def print_graph_arr_j_sem_influenciadores(self):
        print('Grafico de desaparecidos sem influenciadores...')

        arr_desaparecidos_msm_ponto = {}

        x_desaparecido = []
        y_desaparecido = []

        x_perfil = []
        y_perfil = []
        index_perfis = []

        tabela_label = []
        for index_j in self.arr_j_sem_influenciadores:
            x_desaparecido.append(self.desaparecidos[index_j]['lon'])
            y_desaparecido.append(self.desaparecidos[index_j]['lat'])
            try:
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']][self.desaparecidos[index_j]['lat']] += 1
            except:
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']] = {}
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']][self.desaparecidos[index_j]['lat']] = 1

            tabela_label.append(
                {'label': self.database.select_missing(index_j)['name'], 'x': self.desaparecidos[index_j]['lon'],
                 'y': self.desaparecidos[index_j]['lat']})

            for index_i in self.desaparecidos[index_j]['p_area']:
                profile = self.database.select_profile(index_i)

                if index_i not in index_perfis:
                    x_perfil.append(profile['longitude'])
                    y_perfil.append(profile['latitude'])

                    tabela_label.append(
                        {'label': profile['profile_name'], 'x': profile['longitude'], 'y': profile['latitude']})

                    index_perfis.append(index_i)

        print("Numero de desaparecidos sem influenciadores: " + str(len(x_desaparecido)))
        print("Numero de perfis na area: " + str(len(x_perfil)))
        for index_p in index_perfis:
            profile = self.database.select_profile(index_p)
            print(str(profile['profile_name'])),

        # dados
        desaparecidos = (x_desaparecido, y_desaparecido)
        perfis = (x_perfil, y_perfil)

        # agrupa tabela
        tabela_completa = (desaparecidos, perfis)

        # determina cor de cada estado no grafico
        cores = ("blue", "gray")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil")

        # Create plot
        plt.figure()
        # plt.axis((-75, -34, -34, 5))

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        for i, data in enumerate(tabela_label):
            plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

        # titulo do grafico
        plt.title('Desaparecidos sem influenciadores - Desaparecidos:' + str(len(x_desaparecido)) + ' Perfis: ' + str(
            len(x_perfil)))

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('resultados/graficos_analise_desaparecidos_sem_influenciador_sem_label.pdf')
        plt.show()
        print('Done!')

    def print_graph_arr_j_com_influenciadores(self):
        print('Grafico de desaparecidos sem influenciadores...')

        arr_desaparecidos_msm_ponto = {}

        x_desaparecido = []
        y_desaparecido = []

        x_perfil = []
        y_perfil = []
        index_perfis = []

        tabela_label = []
        for index_j in self.arr_j_com_influenciadores:
            x_desaparecido.append(self.desaparecidos[index_j]['lon'])
            y_desaparecido.append(self.desaparecidos[index_j]['lat'])
            try:
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']][self.desaparecidos[index_j]['lat']] += 1
            except:
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']] = {}
                arr_desaparecidos_msm_ponto[self.desaparecidos[index_j]['lon']][self.desaparecidos[index_j]['lat']] = 1

            tabela_label.append(
                {'label': self.database.select_missing(index_j)['name'], 'x': self.desaparecidos[index_j]['lon'],
                 'y': self.desaparecidos[index_j]['lat']})

            for index_i in self.desaparecidos[index_j]['p_area']:
                profile = self.database.select_profile(index_i)

                if index_i not in index_perfis:
                    x_perfil.append(profile['longitude'])
                    y_perfil.append(profile['latitude'])

                    tabela_label.append(
                        {'label': profile['profile_name'], 'x': profile['longitude'], 'y': profile['latitude']})

                    index_perfis.append(index_i)

        print("Numero de desaparecidos com influenciadores: " + str(len(x_desaparecido)))
        print("Numero de perfis na area: " + str(len(x_perfil)))

        # dados
        desaparecidos = (x_desaparecido, y_desaparecido)
        perfis = (x_perfil, y_perfil)

        # agrupa tabela
        tabela_completa = (desaparecidos, perfis)

        # determina cor de cada estado no grafico
        cores = ("blue", "gray")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil")

        # Create plot
        plt.figure()
        # plt.axis((-75, -34, -34, 5))

        for data, color, group in zip(tabela_completa, cores, label):
            x, y = data
            plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        for i, data in enumerate(tabela_label):
            plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

        # titulo do grafico
        plt.title('Desaparecidos com influenciadores - Desaparecidos:' + str(len(x_desaparecido)) + ' Perfis: ' + str(
            len(x_perfil)))

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('resultados/graficos_analise_desaparecidos_com_influenciador_sem_label.pdf')
        plt.show()
        print('Done!')

    def print_graph_by_desaparecido(self):
        print('Creating .graph results...')

        x_desaparecido = {}
        y_desaparecido = {}
        x_perfil_influenciador = {}
        y_perfil_influenciador = {}
        x_perfil_influenciado = {}
        y_perfil_influenciado = {}
        x_perfil_nao_influenciador = {}
        y_perfil_nao_influenciador = {}

        for index_j in self.desaparecidos:
            tabela_label = []
            x_desaparecido[index_j] = self.database.select_missing(index_j)['longitude']
            y_desaparecido[index_j] = self.database.select_missing(index_j)['latitude']
            x_perfil_influenciador[index_j] = []
            y_perfil_influenciador[index_j] = []
            x_perfil_influenciado[index_j] = []
            y_perfil_influenciado[index_j] = []
            x_perfil_nao_influenciador[index_j] = []
            y_perfil_nao_influenciador[index_j] = []
            tabela_label.append({'label': self.database.select_missing(index_j)['name'],
                                 'x': self.database.select_missing(index_j)['longitude'],
                                 'y': self.database.select_missing(index_j)['latitude']})

            for index_i in self.perfis:
                profile = self.database.select_profile(index_i)
                tabela_label.append(
                    {'label': profile['profile_name'], 'x': profile['longitude'], 'y': profile['latitude']})

                try:
                    self.r_ij[index_i][index_j]
                    if self.r_ij[index_i][index_j] == 1.0:
                        x_perfil_influenciador[index_j].append(profile['longitude'])
                        y_perfil_influenciador[index_j].append(profile['latitude'])

                    elif self.d_kj[index_i][index_j] > 0.00001:
                        x_perfil_influenciado[index_j].append(profile['longitude'])
                        y_perfil_influenciado[index_j].append(profile['latitude'])

                    else:
                        x_perfil_nao_influenciador[index_j].append(profile['longitude'])
                        y_perfil_nao_influenciador[index_j].append(profile['latitude'])

                except:
                    pass
                if profile:
                    x_perfil_nao_influenciador[index_j].append(profile['longitude'])
                    y_perfil_nao_influenciador[index_j].append(profile['latitude'])

            if len(x_perfil_influenciador[index_j]) > 0:
                # dados
                desaparecido = ([x_desaparecido[index_j]], [y_desaparecido[index_j]])
                perfil_influenciadores = (x_perfil_influenciador[index_j], y_perfil_influenciador[index_j])
                perfil_influenciado = (x_perfil_influenciado[index_j], y_perfil_influenciado[index_j])
                perfil = (x_perfil_nao_influenciador[index_j], y_perfil_nao_influenciador[index_j])

                # agrupa tabela
                tabela_completa = (desaparecido, perfil_influenciadores, perfil_influenciado, perfil)

                # determina cor de cada estado no grafico
                cores = ("blue", "red", "green")

                # cria um label para os grupos
                label = ("Desaparecido", "Perfil_Influenciador", "Perfil_Influenciado")

                # Create plot
                plt.figure()
                # plt.axis((-75, -34, -34, 5))

                for data, color, group in zip(tabela_completa, cores, label):
                    x, y = data
                    plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

                for i, data in enumerate(tabela_label):
                    plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'],
                             fontsize=9)

                # titulo do grafico
                plt.title('Grafico Desaparecido ' + str(self.database.select_missing(index_j)['name']))

                # insere legenda dos estados
                plt.legend(loc=0)
                plt.savefig('resultados/desaparecido_' + str(index_j) + '_influenciador_influenciados.pdf')

        plt.show()
        print('Done!')


database = postgis_database.Database()
analise = Analise(database)
