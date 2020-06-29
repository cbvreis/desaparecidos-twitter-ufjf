#!/usr/bin/python
# -*- coding: utf-8 -*-
import postgis_database
import math
from tqdm import tqdm
import datetime


class PreProcessamento:

    def __init__(self, database, g, missing_dataset):
        print('PreProcessamento ...')
        inicio = datetime.datetime.now()
        self.database = database
        self.missing_dataset = missing_dataset
        self.graph = g
        self.missing_index = {0}

        self.insert_profile_database()
        self.insert_missing_database()
        self.insert_influences_database()
        fim = datetime.datetime.now()
        print('\n TEMPO DE EXECUÇÃO PRE PROCESSAMENTO: ' + str(fim - inicio))

    def insert_missing_database(self):
        print('\n Insert missing in the database...')
        missing_index = []
        self.database.delete_all_missing()
        for index, line in tqdm(self.missing_dataset.iterrows()):
            if math.isnan(line['lat']) or math.isnan(line['lon']):
                continue
            try:
                self.database.insert_missing(index, line['id'], line['lat'], line['lon'])
                missing_index.append(index)
            except Exception as e:

                pass
        self.missing_index = missing_index

    def insert_profile_database(self):
        print('\n Insert profiles in the database...')
        self.database.delete_all_profile()
        for index_p in tqdm(range(0, len(self.graph.handlers))):

            try:
                self.database.insert_profile(index_p, self.graph.position[index_p]['Perfil'], self.graph.position[index_p]['lat'],
                                       self.graph.position[index_p]['lon'])
            except Exception as e:
                pass

    def insert_influences_database(self):
        print('\n Insert influences in the database...')
        inicio = datetime.datetime.now()
        self.database.delete_all_influences()
        for index_p in tqdm(self.database.select_all_profile()):
            influences = self.graph.get_influencies(index_p, 0.8)
            for influenced_id in influences:
                if self.database.select_profile(influenced_id):
                    self.database.insert_influences(index_p, influenced_id, influences[influenced_id])
        fim = datetime.datetime.now()
        print('TEMPO DE EXECUÇÃO ÁRVORE DE INFLUÊNCIA: ' + str(fim - inicio))

    def get_missing_index(self):
        return self.database.select_all_missing_id()

    def loading_influences(self, l, index_p):
        try:
            influences = self.graph.get_influencies(index_p, 0.8)
        except:
            return
        l.acquire()
        database = postgis_database.Database()
        for influenced_id in influences:
            database.insert_influences(index_p, influenced_id, influences[influenced_id])
        database.close_connection()
        l.release()
