import numpy as np
import json
from joblib import load

def run(record_id, connection):
  if connection:
    return classify(record_id, connection)

def fetch_from_db(query, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        return records
    except Exception as e:
        print(f"Database error: {e}")
        return None

def classify(record_id, connection):
    X = np.load('feature_matrix.npy')
    knn = load('knn_model.joblib')

    id_index_query = f"SELECT array_index FROM id_index WHERE scryfall_id='{record_id}' LIMIT 1"
    record_idx = fetch_from_db(id_index_query, connection)[0][0]

    nearest_neighbor_ids, similarity_scores = find_nearest_neighbors(record_idx, knn, X, connection)

    fetch_data_query = f"SELECT scryfall_id, name, border_crop_url FROM scryfall WHERE scryfall_id = ANY(ARRAY{nearest_neighbor_ids}::uuid[])"
    fetched_data = fetch_from_db(fetch_data_query, connection)

    if fetched_data is None:
        print("Error fetching data.")
        return json.dumps([])

    result = []
    for n_id, score in zip(nearest_neighbor_ids, similarity_scores):
        for rec in fetched_data:
            if rec[0] == n_id:
                result.append({
                    'id': n_id,
                    'name': rec[1],
                    'image_uri': rec[2],
                    'similarity_score': score
                })
                break

    return json.dumps(result)

def find_nearest_neighbors(record_idx, knn_model, X, connection):
    distances, indices = knn_model.kneighbors(X[record_idx].reshape(1, -1))

    indices_str = ','.join([str(i) for i in indices[0]])
    
    id_index_query = f"SELECT scryfall_id FROM id_index WHERE array_index = ANY(ARRAY[{indices_str}])"
    
    fetched_data = fetch_from_db(id_index_query, connection)
    if fetched_data is None:
        print("Error fetching data.")
        return [], []
    
    id_index = [rec[0] for rec in fetched_data]

    neighbors = id_index
    similarity_scores = [round(100 / (1 + d)) for d in distances[0]]
    
    return neighbors, similarity_scores

if __name__ == '__main__':
    from dotenv import load_dotenv
    from pydantic_settings import BaseSettings
    import psycopg2

    load_dotenv('.env.local')

    class Settings(BaseSettings):
        db_host: str = ""
        db_port: int = 5432
        db_name: str = ""
        db_user: str = ""
        db_password: str = ""

    settings = Settings()

    connection = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )

    print(run("000a5154-90ba-459e-b122-d6893dfdb56f", connection))