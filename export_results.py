import csv
import postgis_database
import numpy as np
import matplotlib.pyplot as plt


class Export:
    def __init__(self, database, missing_index, graph, r, d, raio_desaparecido):
        self.database = database
        self.missing_index = missing_index
        self.graph = graph
        self.r = r
        self.d = d
        self.raio_desaparecido = raio_desaparecido
        self.x_desaparecido = {}
        self.y_desaparecido = {}
        self.x_perfil_nao_influenciador = {}
        self.y_perfil_nao_influenciador = {}
        self.x_perfil_influenciado = {}
        self.y_perfil_influenciado = {}
        self.x_perfil_influenciador = {}
        self.y_perfil_influenciador = {}
        self.create_array = False

    def print_csv(self):
        print('Creating .csv results...')
        try:
            csv_perfil_desaparecido = csv.writer(open("resultados/result_perfil_desaparecido.csv", "wb"))
            csv_indices_desaparecido = csv.writer(open("resultados/result_indices_desaparecido.csv", "wb"))
            csv_indices_perfil = csv.writer(open("resultados/result_indices_perfil.csv", "wb"))

            csv_perfil_desaparecido.writerow(
                ["desaparecido_id", "miss_lat", "miss_lon", "Perfil", "Perfil_lat", "Perfil_lon"])
            csv_indices_desaparecido.writerow(["index_j", "desaparecido_id", "raio"])
            csv_indices_perfil.writerow(["index_i", "Perfil"])
        except:
            pass

        for index_i in range(0, len(self.graph.handlers)):
            try:
                if self.graph.position[index_i]:
                    csv_indices_perfil.writerow([str(index_i), str(self.graph.position[index_i]['Perfil'])])

                for index_j in self.missing_index:
                    if index_i == (len(self.graph.handlers) - 1):
                        csv_indices_desaparecido.writerow(
                            [str(index_j), str(self.database.select_missing(index_j)['name']),
                             str(self.raio_desaparecido[index_j])])

                    try:
                        self.r[index_i][index_j]
                        if self.r[index_i][index_j] == 1.0:
                            csv_perfil_desaparecido.writerow(
                                [str(self.database.select_missing(index_j)['name']),
                                 str(self.database.select_missing(index_j)['latitude']),
                                 str(self.database.select_missing(index_j)['longitude']),
                                 str(self.graph.position[index_i]['Perfil']),
                                 str(self.graph.position[index_i]['lat']), str(self.graph.position[index_i]['lon'])])
                    except:
                        pass
            except:
                pass
        print('Done!')

    def print_graph_by_desaparecido(self):
        print('Creating .graph results...')

        for index_j in self.missing_index:
            tabela_label = []
            self.x_desaparecido[index_j] = self.database.select_missing(index_j)['longitude']
            self.y_desaparecido[index_j] = self.database.select_missing(index_j)['latitude']
            self.x_perfil_influenciador[index_j] = []
            self.y_perfil_influenciador[index_j] = []
            self.x_perfil_influenciado[index_j] = []
            self.y_perfil_influenciado[index_j] = []
            self.x_perfil_nao_influenciador[index_j] = []
            self.y_perfil_nao_influenciador[index_j] = []
            tabela_label.append({'label': self.database.select_missing(index_j)['name'],
                                 'x': self.database.select_missing(index_j)['longitude'],
                                 'y': self.database.select_missing(index_j)['latitude']})

            for index_i in range(0, len(self.graph.handlers)):
                if self.graph.position[index_i]:
                    tabela_label.append(
                        {'label': self.graph.position[index_i]['Perfil'], 'x': self.graph.position[index_i]['lon'],
                         'y': self.graph.position[index_i]['lat']})

                try:
                    self.r[index_i][index_j]
                    if self.r[index_i][index_j] == 1.0:
                        self.x_perfil_influenciador[index_j].append(self.graph.position[index_i]['lon'])
                        self.y_perfil_influenciador[index_j].append(self.graph.position[index_i]['lat'])

                    elif self.d[index_i][index_j] != 0:
                        self.x_perfil_influenciado[index_j].append(self.graph.position[index_i]['lon'])
                        self.y_perfil_influenciado[index_j].append(self.graph.position[index_i]['lat'])

                    else:
                        self.x_perfil_nao_influenciador[index_j].append(self.graph.position[index_i]['lon'])
                        self.y_perfil_nao_influenciador[index_j].append(self.graph.position[index_i]['lat'])

                except:
                    if self.graph.position[index_i]:
                        self.x_perfil_nao_influenciador[index_j].append(self.graph.position[index_i]['lon'])
                        self.y_perfil_nao_influenciador[index_j].append(self.graph.position[index_i]['lat'])

            # dados
            desaparecido = ([self.x_desaparecido[index_j]], [self.y_desaparecido[index_j]])
            perfil_influenciadores = (self.x_perfil_influenciador[index_j], self.y_perfil_influenciador[index_j])
            perfil_influenciado = (self.x_perfil_influenciado[index_j], self.y_perfil_influenciado[index_j])
            perfil = (self.x_perfil_nao_influenciador[index_j], self.y_perfil_nao_influenciador[index_j])

            # agrupa tabela
            tabela_completa = (desaparecido, perfil_influenciadores, perfil_influenciado, perfil)

            # determina cor de cada estado no grafico
            cores = ("blue", "red", "green", "gray")

            # cria um label para os grupos
            label = ("Desaparecido", "Perfil_Influenciador", "Perfil_Influenciado", "Perfil")

            # Create plot
            plt.figure()
            # plt.axis((-75, -34, -34, 5))

            for data, color, group in zip(tabela_completa, cores, label):
                x, y = data
                plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

            for i, data in enumerate(tabela_label):
                plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

            # titulo do grafico
            plt.title('Grafico Desaparecido ' + str(self.database.select_missing(index_j)['name']))

            # insere legenda dos estados
            plt.legend(loc=0)
            plt.savefig('graficos/' + str(index_j) + '.pdf')

        plt.show()
        print('Done!')

    def print_graph_desaparecidos_perfis(self):
        print('Creating .graph results...')

        x_desaparecido = []
        y_desaparecido = []
        x_perfil = []
        y_perfil = []
        tabela_label = []
        for index_j in self.missing_index:
            try:
                x_desaparecido.append(self.database.select_missing(index_j)['longitude'])
                y_desaparecido.append(self.database.select_missing(index_j)['latitude'])

                tabela_label.append({'label': self.database.select_missing(index_j)['name'],
                                     'x': self.database.select_missing(index_j)['longitude'],
                                     'y': self.database.select_missing(index_j)['latitude']})
            except:
                pass

        for index_i in range(0, len(self.graph.handlers)):
            try:
                x_perfil.append(self.graph.position[index_i]['lon'])
                y_perfil.append(self.graph.position[index_i]['lat'])
                tabela_label.append(
                    {'label': self.graph.position[index_i]['Perfil'], 'x': self.graph.position[index_i]['lon'],
                    'y': self.graph.position[index_i]['lat']})
            except:
                pass

        # dados
        desaparecido = ([x_desaparecido], [y_desaparecido])
        perfil = (x_perfil, y_perfil)

        # agrupa tabela
        tabela_completa = (desaparecido, perfil)

        # determina cor de cada estado no grafico
        cores = ("blue", "red", "gray")

        # cria um label para os grupos
        label = ("Desaparecido", "Perfil")

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
        plt.title('Grafico Desaparecido e Perfis ')

        # insere legenda dos estados
        plt.legend(loc=0)
        plt.savefig('graficos/desaparecidos_e_perfis.pdf')
        plt.show()
        print('Done!')


    def print_influencias_perfis(self):
        print('Creating .graph results...')

        tabela_label = []
        self.x_perfil_influenciador = {}
        self.y_perfil_influenciador = {}
        for index_i in range(0, len(self.graph.handlers)):
            profile_influenciador = self.database.select_profile(index_i)
            self.x_perfil_influenciador[index_i] = profile_influenciador['longitude']
            self.y_perfil_influenciador[index_i] = profile_influenciador['latitude']

            self.x_perfil_influenciado[index_i] = []
            self.y_perfil_influenciado[index_i] = []

            tabela_label.append(
                    {'label': profile_influenciador['profile_name'], 'x': profile_influenciador['longitude'],
                     'y': profile_influenciador['latitude']})

            influenceds = self.database.select_influences_by_influencer(index_i)
            for index in influenceds:
                influenciado = self.database.select_profile(index)
                self.y_perfil_influenciado[index_i].append(influenciado['longitude'])
                self.y_perfil_influenciado[index_i].append(influenciado['latitude'])

                tabela_label.append(
                    {'label': influenciado['profile_name'], 'x': influenciado['longitude'],
                     'y': influenciado['latitude']})

            # dados
            perfil_influenciadores = ([self.x_perfil_influenciador[index_i]], [self.y_perfil_influenciador[index_i]])
            perfil_influenciado = (self.x_perfil_influenciado[index_i], self.y_perfil_influenciado[index_i])

            # agrupa tabela
            tabela_completa = (perfil_influenciadores, perfil_influenciado)

            # determina cor de cada estado no grafico
            cores = ("red", "green")

            # cria um label para os grupos
            label = ("Perfil_Influenciador", "Perfil Influenciado")

            # Create plot
            plt.figure()
            # plt.axis((-75, -34, -34, 5))

            for data, color, group in zip(tabela_completa, cores, label):
                x, y = data
                plt.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

            for i, data in enumerate(tabela_label):
                plt.text(tabela_label[i]['x'] - 0.05, tabela_label[i]['y'] - 0.05, tabela_label[i]['label'], fontsize=9)

            # titulo do grafico
            plt.title('Grafico Perfil ' + str(self.database.select_missing(index_i)['name']))

            # insere legenda dos estados
            plt.legend(loc=0)
            plt.savefig('graficos/' + str(index_i) + '.pdf')

        plt.show()
        print('Done!')
