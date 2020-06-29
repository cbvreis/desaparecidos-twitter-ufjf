import pandas as pd
import numpy as np
from tqdm import tqdm
import math


class Graph:

    def __init__(self, input_file_profile):
        # Loads CSV file with information about relationships
        dataset = pd.read_csv(input_file_profile, header=0, encoding='latin1')
        dataset.dropna(thresh=2)

        # Checks for unique Twitter handlers and selects the unique
        self.handlers = np.concatenate((dataset['Perfil'].unique(), dataset['Seguidor'].unique()))
        self.handlers = sorted(np.unique(self.handlers))

        print('Creating index...')
        self.inversed = {}
        for index, handler in tqdm(enumerate(self.handlers)):
            self.inversed[handler] = index

        self.relationships = {}
        self.adjacencies = {}
        self.influencers = {}
        self.position = {}
        for index, handler in enumerate(self.handlers):
            self.relationships[index] = {}
            self.adjacencies[index] = []
            self.position[index] = []

        print('Loading relationships and distance...')
        for index, row in tqdm(dataset.iterrows()):
            if math.isnan(row['lat']) or math.isnan(row['lon']):
                continue
            self.relationships[self.inversed[row['Perfil']]][self.inversed[row['Seguidor']]] = row['Peso']
            self.adjacencies[self.inversed[row['Perfil']]].append(self.inversed[row['Seguidor']])
            self.position[self.inversed[row['Perfil']]] = {'Perfil': row['Perfil'], 'lat': row['lat'],
                                                           'lon': row['lon']}
        print('Done!')
        print(len(self.inversed))

    def get_weight(self, id_a, id_b):
        try:
            weight = self.relationships[id_b][id_a]
        except:
            weight = 0
        return weight

    def get_adjacency(self, id):
        return self.adjacencies[id]
    
    def get_inversed_adjacency(self, id):
        return self.influencers[id]

    def get_influencies(self, id, information_cut):
        influences = {id: 1.0}
        influences_return = {id: 1.0}
        queue = [id]
        while len(queue) > 0:
            front = queue.pop(0)

            for node in self.get_adjacency(front):
                if node not in queue:
                    try:
                        influences[node]
                        pass
                    except:
                        influences[node] = influences[front] * self.get_weight(node, front)
                        if influences[node] >= information_cut:
                            influences_return[node] = influences[node]
                            queue.append(node)

        return influences_return
    
    def get_inversed_influencies(self, id, information_cut):
        influences = {id: 1.0}
        influences_return = {id: 1.0}
        queue = [id]
        while len(queue) > 0:
            front = queue.pop(0)

            for node in self.get_inversed_adjacency(front):
                if node not in queue:
                    try:
                        influences[node]
                        pass
                    except:
                        influences[node] = influences[front] * self.get_weight(node, front)
                        if influences[node] >= information_cut:
                            influences_return[node] = influences[node]
                            queue.append(node)

        return influences_return

    def get_distance_profile_missing(self, index_k, miss_latitude, miss_longitude, raio):

        perfil_latitude = self.position[index_k]['lat']
        perfil_longitude = self.position[index_k]['lon']

        if math.isnan(perfil_latitude) == True and math.isnan(perfil_longitude) == True and math.isnan(
                miss_longitude) == True and math.isnan(miss_latitude) == True:
            return 0

        perfil_latitude = math.radians(float(perfil_latitude))
        perfil_longitude = math.radians(float(perfil_longitude))
        miss_latitude = math.radians(float(miss_latitude))
        miss_longitude = math.radians(float(miss_longitude))

        if perfil_latitude == miss_latitude and perfil_longitude == miss_longitude:
            return 1

        distance = (6371 * math.asin(math.cos(perfil_latitude) * math.cos(miss_latitude) * math.cos(
            miss_longitude - perfil_longitude) + math.sin(perfil_latitude) * math.sin(miss_latitude)))
        print(distance)
        return 1 / distance

    def get_distance_eucladiana(self, index_k, miss_latitude, miss_longitude, raio):
        perfil_latitude = self.position[index_k]['lat']
        perfil_longitude = self.position[index_k]['lon']

        if math.isnan(perfil_latitude) == True and math.isnan(perfil_longitude) == True and math.isnan(
                miss_longitude) == True and math.isnan(miss_latitude) == True:
            return 0

        perfil_latitude = math.radians(float(perfil_latitude))
        perfil_longitude = math.radians(float(perfil_longitude))
        miss_latitude = math.radians(float(miss_latitude))
        miss_longitude = math.radians(float(miss_longitude))

        if perfil_latitude == miss_latitude and perfil_longitude == miss_longitude:
            return 1


        distance = math.sqrt((perfil_latitude - miss_latitude) ** 2 + (perfil_longitude - miss_longitude))
        print(distance)
        return distance
