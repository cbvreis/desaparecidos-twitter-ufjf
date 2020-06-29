import psycopg2
import math
import time


class Database:

    def __init__(self):
        con = psycopg2.connect(host='localhost', database='perfil_twitter', user='admin', password='admin')
        cur = con.cursor()

        self.connection = con
        self.cursor = cur

    def close_connection(self):
        self.connection.close()

    def insert_profile(self, index_p, profile, lat, lon):
        if math.isnan(lat) == False and math.isnan(
                lon) == False and lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180:
            sql = "INSERT INTO profile VALUES (" + str(index_p) + ",'" + str(profile) + "','POINT(" + str(
                lon) + " " + str(lat) + ")')"
            try:
                self.cursor.execute(sql)
                self.connection.commit()
            except:
                pass

    def insert_missing(self, index, name, latitude, longitude):
        if math.isnan(latitude) == False and math.isnan(longitude) == False:
            sql = "INSERT INTO missing(id, name, coordinate) VALUES (" + str(index) + ",'" + str(
                name) + "','POINT(" + str(
                longitude) + " " + str(latitude) + ")')"
            try:
                self.cursor.execute(sql)
                self.connection.commit()
            except:
                pass

    def insert_influences(self, influencer_id, influenced_id, value):
        sql = "INSERT INTO influences(influencer, influenced, value) VALUES (" + str(influencer_id) + "," + str(
            influenced_id) + ", " + str(value) + ")"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except psycopg2.OperationalError as e:
            pass

    def insert_result_r(self, index_i, index_j, value):
        sql = "INSERT INTO result_r(profile_i, missing_j, value) VALUES (" + str(index_i) + "," + str(
            index_j) + ", " + str(value) + ")"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except psycopg2.OperationalError as e:
            print('ERRO')
            print(e)
            pass

    def insert_result_dj(self, index_j, value):
        sql = "INSERT INTO result_dj(missing_j, value) VALUES (" + str(index_j) + ", " + str(value) + ")"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except psycopg2.OperationalError as e:
            print('ERRO')
            print(e)
            pass

    def insert_result_dkj(self, index_k, index_j, value):
        sql = "INSERT INTO result_dkj(profile_k, missing_j, value) VALUES (" + str(index_k) + "," + str(
            index_j) + ", " + str(value) + ")"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except psycopg2.OperationalError as e:
            print('ERRO')
            print(e)
            pass

    def insert_raio_missing(self, index_j, raio):
        sql = "INSERT INTO raio_missing(missing_j, value) VALUES (" + str(index_j) + ", " + str(raio) + ")"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except psycopg2.OperationalError as e:
            pass

    def select_profile_raio(self, index_j, raio, person_region):
        missing = self.select_missing(index_j)

        arr_perfil = self.select_dwithin(missing['latitude'], missing['longitude'], raio)

        while len(arr_perfil) < person_region:
            raio = raio * 5
            arr_perfil = self.select_dwithin(missing['latitude'], missing['longitude'], raio)

        return arr_perfil, raio

    def select_missing_raio(self, index_j, raio):
        arr_index_missing = []
        missing = self.select_missing(index_j)
        sql = "SELECT * FROM missing as m WHERE ST_DWITHIN(m.coordinate,'POINT(" + str(
            missing['longitude']) + " " + str(
            missing['latitude']) + ")', " + str(raio) + ")"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_index_missing.append(row[0])
        except NameError:
            pass
        return arr_index_missing

    def select_dwithin(self, miss_latitude, miss_longitude, raio):
        arr_index_profile = []
        sql = "SELECT * FROM profile as p WHERE ST_DWITHIN(p.coordinate,'POINT(" + str(miss_longitude) + " " + str(
            miss_latitude) + ")', " + str(raio) + ")"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_index_profile.append(row[0])
        except NameError:
            pass

        return arr_index_profile

    def select_distance(self, p1_latitude, p1_longitude, p2_latitude, p2_longitude, raio=1):
        distance = None
        sql = "SELECT ST_Distance('POINT(" + str(p1_longitude) + " " + str(p1_latitude) + ")'::geography,'POINT(" + str(
            p2_longitude) + " " + str(p2_latitude) + ")'::geography)"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            distance = select_result[0]
        except NameError:
            pass
        if distance == 0:
            return distance
        return 5000000 / distance

    def select_distance_with_raio_max(self, p1_latitude, p1_longitude, p2_latitude, p2_longitude, raio_max):
        distance_p1_p2 = 0
        sql = "SELECT ST_Distance('POINT(" + str(p1_longitude) + " " + str(p1_latitude) + ")'::geography,'POINT(" + str(
            p2_longitude) + " " + str(p2_latitude) + ")'::geography)"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            distance_p1_p2 = select_result[0]
        except NameError:
            pass

        return (raio_max - distance_p1_p2)/raio_max

    def select_dwithin_regions(self, miss_latitude, miss_longitude, raio_inicial, raio_region):
        arr_index_profile = []
        sql = "SELECT * FROM (SELECT * FROM profile as p WHERE ST_DWITHIN(p.coordinate,'POINT(" + str(
            miss_longitude) + " " + str(
            miss_latitude) + ")', " + str(raio_inicial) + ")) as p2 WHERE ST_DWITHIN(p2.coordinate,'POINT(" + str(
            miss_longitude) + " " + str(
            miss_latitude) + ")', " + str(raio_region) + ")"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_index_profile.append(row[0])
        except NameError:
            pass

        return arr_index_profile

    def select_missing(self, id):
        missing = {}
        sql = "SELECT id, name, ST_X(coordinate::geometry) as longitude, ST_Y(coordinate::geometry) as latitude FROM public.missing WHERE id =" + str(
            id)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if select_result == None:
                return missing
            missing = {'id': select_result[0], 'name': select_result[1], 'longitude': select_result[2],
                       'latitude': select_result[3]}
        except NameError:
            pass

        return missing

    def select_missing_by_lon_lat(self, lon, lat):
        arr_index_missing = []
        sql = "SELECT id FROM public.missing as m WHERE m.coordinate = 'POINT(" + str(lon) + " " + str(lat) + ")'"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_index_missing.append(row[0])
        except NameError:
            pass
        return arr_index_missing

    def select_profile(self, id):
        profile = {}
        sql = "SELECT id, profile_name, ST_X(coordinate::geometry) as longitude, ST_Y(coordinate::geometry) as latitude FROM public.profile WHERE id =" + str(
            id)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                return None

            profile = {'id': select_result[0], 'profile_name': select_result[1], 'longitude': select_result[2],
                       'latitude': select_result[3]}
        except NameError:
            pass

        return profile

    def select_influences(self, influencer, influenced):
        influence = None
        sql = "SELECT value FROM influences where influencer = " + str(influencer) + " and influenced =" + str(
            influenced)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            influence = select_result[0]
        except NameError:
            pass

        return influence

    def select_influences_by_influencer(self, influencer):
        influences = {}
        sql = "SELECT * FROM influences where influencer = " + str(influencer)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                influences[row[1]] = row[2]
        except NameError:
            pass

        return influences

    def select_influences_by_influenced(self, influenced):
        influences = {}
        sql = "SELECT * FROM influences where influenced = " + str(influenced)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                influences[row[0]] = row[2]
        except NameError:
            pass

        return influences

    def select_network_profile(self, id):
        arr_index_profiles = []
        sql = "SELECT * FROM influences where influenced = " + str(id) + " or influencer = " + str(id) + ""
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                if row[0] not in arr_index_profiles:
                    arr_index_profiles.append(row[0])
                if row[1] not in arr_index_profiles:
                    arr_index_profiles.append(row[1])
        except NameError:
            pass

        return arr_index_profiles

    def select_all_missing_id(self):
        arr_missing = []
        sql = "SELECT id FROM public.missing"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_missing.append(row[0])
        except NameError:
            pass
        return arr_missing

    def select_network_profiles(self, arr_profile_id):
        arr_network_profiles = []
        if len(arr_profile_id) == 1:
            t_profile_id = "(" + str(arr_profile_id[0]) + ")"
        else:
            t_profile_id = tuple(arr_profile_id)

        sql = "SELECT * FROM influences where influenced in " + str(t_profile_id) + " or influencer in " + str(
            t_profile_id) + ""
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                if row[0] not in arr_network_profiles:
                    arr_network_profiles.append(row[0])
                if row[1] not in arr_network_profiles:
                    arr_network_profiles.append(row[1])
        except NameError:
            pass

        return arr_network_profiles

    def select_result_r(self, index_i, index_j):
        result_r = None
        sql = "SELECT value FROM public.result_r WHERE missing_j =" + str(index_j) + " and profile_i = " + str(index_i)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                return None
            result_r = select_result[0]
        except NameError:
            pass

        return result_r

    def select_result_r_by_profile(self, index_i):
        result_r = {}
        sql = "SELECT missing_j, value FROM public.result_r WHERE profile_i = " + str(index_i)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                result_r[row[0]] = row[1]

        except NameError:
            pass
        return result_r

    def select_result_r_lagger_0(self):
        result_r = {}
        sql = "SELECT profile_i, missing_j, value FROM public.result_r WHERE value > 0"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            arr_index_i = []
            for row in select_result:
                if row[0] not in arr_index_i:
                    result_r[row[0]] = {}
                    arr_index_i.append(row[0])

                result_r[row[0]][row[1]] = row[2]

        except psycopg2.OperationalError as e:
            print('ERRO')
            print(e)
            pass
        return result_r

    def select_result_dkj(self, index_k, index_j):
        result_dkj = None
        sql = "SELECT value FROM public.result_dkj WHERE missing_j =" + str(index_j) + " and profile_k = " + str(
            index_k)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                return None
            result_dkj = select_result[0]
        except NameError:
            pass

        return result_dkj

    def select_result_dkj_by_missing(self, index_j):
        result_dkj = {}
        sql = "SELECT profile_k, missing_j, value FROM public.result_dkj WHERE missing_j =" + str(index_j)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            arr_index_i = []
            for row in select_result:
                if row[0] not in arr_index_i:
                    result_dkj[row[0]] = {}
                    arr_index_i.append(row[0])

                result_dkj[row[0]][row[1]] = row[2]
        except NameError:
            pass

        return result_dkj

    def select_influenced_profiles_by_missing(self, index_j):
        profiles = 0
        sql = "select profile_k from result_dkj where value > 0 and missing_j =" + str(index_j)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            profiles = len(select_result)
        except NameError:
            pass

        return profiles

    def select_influenced_profiles_by_missing_raio(self, index_j, raio):
        profiles = 0
        arr_profiles_raio, raio_aux = self.select_profile_raio(index_j, raio, 1)

        if len(arr_profiles_raio) == 1:
            t_profile_id = "(" + str(arr_profiles_raio[0]) + ")"
        else:
            # t_profile_id = tuple(map(tuple, arr_profiles_raio))
            t_profile_id = tuple(arr_profiles_raio)
        sql = "select profile_k from result_dkj where value > 0 and missing_j =" + str(
            index_j) + " and profile_k IN " + str(t_profile_id)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            profiles = len(select_result)
        except NameError:
            pass
        return profiles

    def select_result_dj(self, index_j):
        result_dj = None
        sql = "SELECT value FROM public.result_dj WHERE missing_j =" + str(index_j)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                return None
            result_dj = select_result[0]
        except NameError:
            pass

        return result_dj

    # 20 000 a 40 000 vazio
    def select_all_value_result_dj(self):
        arr_value = []
        sql = "SELECT value FROM public.result_dj where value > 0"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                # if 200000 <= row[0]:
                if 0 <= row[0] <= 1500:
                    arr_value.append(row[0])
        except NameError:
            pass
        return arr_value

    def select_raio_missing(self, index_j):
        raio = None
        sql = "SELECT value FROM public.raio_missing WHERE missing_j =" + str(index_j)
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                return None
            raio = select_result[0]
        except NameError:
            pass
        return raio

    def select_all_result_r(self):
        result_r = {}
        sql = "SELECT profile_i, missing_j, value FROM public.result_r "
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                if not result_r[row[0]]:
                    result_r[row[0]] = {}
                result_r[row[0]][row[1]] = row[2]
        except NameError:
            pass

        return result_r

    def select_all_missing(self):
        arr_missing = {}
        sql = "SELECT id, name, ST_X(coordinate::geometry) as longitude, ST_Y(coordinate::geometry) FROM public.missing"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_missing[row[0]] = {}
                arr_missing[row[0]] = {'id': row[0], 'name': row[1], 'longitude': row[2], 'latitude': row[3]}
        except NameError:
            pass
        return arr_missing

    def select_all_profile(self):
        arr_profile = {}
        sql = "SELECT id, profile_name, ST_X(coordinate::geometry) as longitude, ST_Y(coordinate::geometry) FROM public.profile"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchall()
            for row in select_result:
                arr_profile[row[0]] = {}
                arr_profile[row[0]] = {'id': row[0], 'profile_name': row[1], 'longitude': row[2], 'latitude': row[3]}
        except NameError:
            pass
        return arr_profile

    def select_larger_missing_raio(self):
        sql = "select MAX(value) from raio_missing"
        try:
            self.cursor.execute(sql)
            select_result = self.cursor.fetchone()
            return select_result[0]
        except:
            pass

    def delete_all_profile_not_in(self, arr_profile_id):
        t_profile_id = tuple(arr_profile_id)
        sql = "DELETE FROM profile WHERE id NOT IN " + str(t_profile_id)
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_profile(self):
        sql = "DELETE FROM profile WHERE id IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_missing(self):
        sql = "DELETE FROM missing WHERE id IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_influences(self):
        sql = "DELETE FROM influences WHERE influencer IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_result_r(self):
        sql = "DELETE FROM result_r WHERE missing_j IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_result_dkj(self):
        sql = "DELETE FROM result_dkj WHERE missing_j IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_result_dj(self):
        sql = "DELETE FROM result_dj WHERE missing_j IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass

    def delete_all_raio_missing(self):
        sql = "DELETE FROM raio_missing WHERE missing_j IS NOT NULL"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except NameError:
            pass
