import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump, load

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_dict = {'id': [], 'cmc': []}
for col in ['W', 'U', 'B', 'R', 'G']:
    data_dict[col] = []

names = []
oracle_texts = []  # List to store oracle_text
type_lines = []  # List to store type_line
sets = []  # List to store sets
flavor_texts = []  # List to store flavor_texts

all_keywords = set()
processed_names = set()
unique_data = []

for record in data:
    name = record.get('name', '')
    if name in processed_names:
        continue
    processed_names.add(name)
    names.append(name)
    oracle_texts.append(record.get('oracle_text', ''))  # Collect oracle_text
    type_lines.append(record.get('type_line', ''))  # Collect type_line
    sets.append(record.get('set', ''))
    flavor_texts.append(record.get('flavor_text', ''))

    unique_data.append(record)

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

for i, record in enumerate(unique_data):
    keywords = record.get('keywords', [])
    for keyword in keywords:
        if keyword in all_keywords:
            data_dict[keyword][i] = 1

df_filtered = pd.DataFrame(data_dict)

vectorizer = CountVectorizer(max_features=1500)
name_matrix = vectorizer.fit_transform(names)
name_array = name_matrix.toarray()

# Vectorize oracle_text
oracle_vectorizer = CountVectorizer(max_features=1500)
oracle_matrix = oracle_vectorizer.fit_transform(oracle_texts)
oracle_array = oracle_matrix.toarray()

# Apply CountVectorizer to type_lines
type_vectorizer = CountVectorizer(max_features=500)
type_matrix = type_vectorizer.fit_transform(type_lines)
type_array = type_matrix.toarray()

# Vectorize set
set_vectorizer = CountVectorizer(max_features=1000)
set_matrix = set_vectorizer.fit_transform(sets)
set_array = set_matrix.toarray()

# Vectorize flavor_text
flavor_text_vectorizer = CountVectorizer(max_features=1500)
flavor_text_matrix = flavor_text_vectorizer.fit_transform(flavor_texts)
flavor_text_array = flavor_text_matrix.toarray()

X = np.hstack([
    df_filtered.drop('id', axis=1).values, 
    name_array, 
    oracle_array, 
    type_array, 
    set_array,
    flavor_text_array
])
id_index = df_filtered['id'].tolist()

k = 25
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X, id_index)

# Create an id_to_name_and_image mapping
id_to_name_and_image = {record.get('id', ''): {'name': record.get('name', ''), 'image_uri': record.get('image_uris', {}).get('border_crop', '')} for record in unique_data}

# Save the id_to_name_and_image mapping
with open('id_to_name_and_image.json', 'w') as f:
    json.dump(id_to_name_and_image, f)

# Save the feature matrix X and id_index
np.save('feature_matrix.npy', X)
with open('id_index.json', 'w') as f:
    json.dump(id_index, f)

# Save the model
dump(knn, 'knn_model.joblib')

# test #

def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    similarity_scores = [round(1 + 99 * (1 / (1 + d))) for d in distances[0]]
    return neighbors, similarity_scores

record_id = 'a575a9af-e1de-4a1d-91d8-440585377e4f'  # Replace with an actual id from your data
nearest_neighbor_ids, similarity_scores = find_nearest_neighbors(record_id, id_index, knn, X)

nearest_neighbor_names_and_images = [id_to_name_and_image.get(n_id, {'name': '', 'image_uri': ''}) for n_id in nearest_neighbor_ids]

print(f"Nearest neighbors to ID {record_id} are:")
for n_id, n_dict, score in zip(nearest_neighbor_ids, nearest_neighbor_names_and_images, similarity_scores):
    print(f"Name: {n_dict['name']}, Image URI: {n_dict['image_uri']}, Similarity Score: {score}")


