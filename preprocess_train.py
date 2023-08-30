import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import KNeighborsClassifier

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_dict = {'id': [], 'cmc': []}
for col in ['W', 'U', 'B', 'R', 'G']:
    data_dict[col] = []

names = []

all_keywords = set()
processed_names = set()
unique_data = []

for record in data:
    name = record.get('name', '')
    if name in processed_names:
        continue
    processed_names.add(name)
    names.append(name)
    
    unique_data.append(record)  # Only add unique records to this list
    
    data_dict['id'].append(record.get('id', ''))
    data_dict['cmc'].append(record.get('cmc', 0))
    for col in ['W', 'U', 'B', 'R', 'G']:
        data_dict[col].append(0)

    colors = record.get('colors', [])
    for col in colors:
        if col in ['W', 'U', 'B', 'R', 'G']:
            data_dict[col][-1] = 1

    keywords = record.get('keywords', [])
    all_keywords.update(keywords)

for keyword in all_keywords:
    data_dict[keyword] = [0] * len(data_dict['id'])

# Use unique_data instead of data for this loop
for i, record in enumerate(unique_data):
    keywords = record.get('keywords', [])
    for keyword in keywords:
        if keyword in all_keywords:
            data_dict[keyword][i] = 1

df_filtered = pd.DataFrame(data_dict)

vectorizer = CountVectorizer(max_features=1000)
name_matrix = vectorizer.fit_transform(names)
name_array = name_matrix.toarray()

X = np.hstack([df_filtered.drop('id', axis=1).values, name_array])
id_index = df_filtered['id'].tolist()

k = 25
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X, id_index)

def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    return neighbors

record_id = '230281e4-1cee-4cf8-a73c-63a21c5eb60b'
nearest_neighbor_ids = find_nearest_neighbors(record_id, id_index, knn, X)
id_to_name = {record.get('id', ''): record.get('name', '') for record in unique_data}
nearest_neighbor_names = [id_to_name.get(n_id, '') for n_id in nearest_neighbor_ids]

print(f"Nearest neighbors to ID {record_id} are:")
for n_id, n_name in zip(nearest_neighbor_ids, nearest_neighbor_names):
    print(f"ID: {n_id}, Name: {n_name}")
