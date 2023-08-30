from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np
import json

# Load the JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Assume df_filtered is already created and saved
df_filtered = pd.read_csv('processed_data.csv')

# Extract feature matrix and id_index
X = df_filtered.drop('id', axis=1).to_numpy()
id_index = df_filtered['id'].to_list()

# Create a dictionary to map 'id' to 'name' from the original JSON data
id_to_name = {record.get('id', ''): record.get('name', '') for record in data}

# Initialize k-NN model
k = 15  # number of neighbors
knn = KNeighborsClassifier(n_neighbors=k)

# Train the model
knn.fit(X, id_index)

# Function to find nearest neighbors
def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    return neighbors

# Query example
record_id = '0000579f-7b35-4ed3-b44c-db2a538066fe'  # Replace with an actual id from your data
nearest_neighbor_ids = find_nearest_neighbors(record_id, id_index, knn, X)

# Retrieve names for the nearest neighbor ids
nearest_neighbor_names = [id_to_name[n_id] for n_id in nearest_neighbor_ids]

print(f"Nearest neighbors to ID {record_id} are:")
for n_id, n_name in zip(nearest_neighbor_ids, nearest_neighbor_names):
    print(f"ID: {n_id}, Name: {n_name}")
