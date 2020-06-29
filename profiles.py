import matplotlib.pyplot as plt
import pandas as pd
import graph
import postgis_database
from pre_processamento import PreProcessamento
from tqdm import tqdm

database = postgis_database.Database()

# Reads twitter profile from CSV
g = graph.Graph('dataset/teste/b_perfis_teste_2.csv')
pre_processamento = PreProcessamento(database, g, [])
missing_index = pre_processamento.get_missing_index()

perfis = {}

all_profile = database.select_all_profile()
for index_p in tqdm(all_profile):

    perfis[index_p] = {'latitude': all_profile[index_p]['latitude'], 'longitude':
        all_profile[index_p]['longitude'], 'label': all_profile[index_p]['profile_name']}

plt.figure()
for index in perfis:
    qnt_influenced = len(database.select_influences_by_influencer(index))
    print(str(index)+' => '+str(perfis[index]['label'])+' => '+str(qnt_influenced))
    plt.scatter(perfis[index]['longitude'], perfis[index]['latitude'], alpha=0.8, c='blue', edgecolors='b', s=(20 *qnt_influenced ))

for index in perfis:
    plt.text(perfis[index]['longitude'] - 0.05, perfis[index]['latitude'] - 0.05, perfis[index]['label'], fontsize=9)

# titulo do grafico
plt.title('Grafico Perfil')

# insere legenda dos estados
plt.savefig('graficos_perfis/perfis.pdf')
plt.show()
print('Done!')
