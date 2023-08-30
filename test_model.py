import numpy as np
import json
from joblib import load

def classify(record_id):
  # Load the saved feature matrix and id_index
  X = np.load('feature_matrix.npy')
  with open('id_index.json', 'r') as f:
      id_index = json.load(f)

  # Load the saved KNN model
  knn = load('knn_model.joblib')

  # Load the id_to_name_and_image mapping
  with open('id_to_name_and_image.json', 'r') as f:
    id_to_name_and_image = json.load(f)

  # Example record_id to find nearest neighbors for
  # record_id = '5bb3cb5c-8d66-4f5e-a9a9-917e6045f024'  # Replace this with an actual ID from your data

  # Find the nearest neighbors and similarity scores
  nearest_neighbor_ids, similarity_scores = find_nearest_neighbors(record_id, id_index, knn, X)

  # Retrieve the names and image_uris of the nearest neighbors
  nearest_neighbor_names_and_images = [id_to_name_and_image.get(n_id, {'name': '', 'image_uri': ''}) for n_id in nearest_neighbor_ids]

  # Create a list of dictionaries for the result
  result = []
  for n_id, n_dict, score in zip(nearest_neighbor_ids, nearest_neighbor_names_and_images, similarity_scores):
    result.append({
        'id': n_id,
        'name': n_dict['name'],
        'image_uri': n_dict['image_uri'],
        'similarity_score': score
    })

  # Return the list of dictionaries as a JSON-serializable string
  return json.dumps(result)

# Function to find nearest neighbors and similarity scores
def find_nearest_neighbors(record_id, id_index, knn_model, X):
    record_idx = id_index.index(record_id)
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))
    neighbors = [id_index[i] for i in indices[0]]
    similarity_scores = [round(100 / (1 + d)) for d in distances[0]]
    return neighbors, similarity_scores
