import numpy as np
import json
from sklearn.neighbors import KNeighborsClassifier
from joblib import load

# Function to find nearest neighbors and similarity scores
def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    similarity_scores = [round(100 / (1 + d)) for d in distances[0]]
    return neighbors, similarity_scores

# Load the saved feature matrix and id_index
X = np.load('feature_matrix.npy')
with open('id_index.json', 'r') as f:
    id_index = json.load(f)

# Load the saved KNN model
knn = load('knn_model.joblib')

# Load the id_to_name mapping (assuming you saved it as a JSON)
with open('id_to_name.json', 'r') as f:
    id_to_name = json.load(f)

# Example record_id to find nearest neighbors for
record_id = '5bb3cb5c-8d66-4f5e-a9a9-917e6045f024'  # Replace this with an actual ID from your data

# Find the nearest neighbors and similarity scores
nearest_neighbor_ids, similarity_scores = find_nearest_neighbors(record_id, id_index, knn, X)

# Retrieve the names of the nearest neighbors
nearest_neighbor_names = [id_to_name.get(n_id, '') for n_id in nearest_neighbor_ids]

# Display the results
print(f"Nearest neighbors to ID {record_id} are:")
for n_id, n_name, score in zip(nearest_neighbor_ids, nearest_neighbor_names, similarity_scores):
    print(f"Name: {n_name}, Similarity Score: {score}")
