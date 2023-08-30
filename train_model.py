from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np

df_filtered = pd.read_csv('processed_data.csv')

X = df_filtered.drop('id', axis=1).to_numpy()
id_index = df_filtered['id'].to_list()

k = 5  # number of neighbors
knn = KNeighborsClassifier(n_neighbors=k)

knn.fit(X, id_index)

def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    return neighbors

# Sample query
record_id = 'b81c6c8b-a9cf-4866-89ba-7f8ad077b836'
nearest_neighbors = find_nearest_neighbors(record_id, id_index, knn, X)
print(f"Nearest neighbors to {record_id} are {nearest_neighbors}")
