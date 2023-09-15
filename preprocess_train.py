import pandas as pd
from scipy.sparse import hstack, save_npz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump
import gzip
import json

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

def connect_to_db(settings):
    try:
        connection = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password
        )
        return connection
    except Exception as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None
    
def upsert_data_to_db(connection, unique_data):
    cursor = connection.cursor()
    batch_size = 1000

    query = '''
        INSERT INTO scryfall (scryfall_id, name, type_line, set, flavor_text, oracle_text, border_crop_url)
        VALUES %s
        ON CONFLICT (scryfall_id) DO UPDATE
        SET name = EXCLUDED.name,
            type_line = EXCLUDED.type_line,
            set = EXCLUDED.set,
            flavor_text = EXCLUDED.flavor_text,
            oracle_text = EXCLUDED.oracle_text,
            border_crop_url = EXCLUDED.border_crop_url;
    '''

    for i in range(0, len(unique_data), batch_size):
        batch = unique_data[i:i + batch_size]
        values = [(record.get('id'), 
                   record.get('name'),
                   record.get('type_line'),
                   record.get('set'),
                   record.get('flavor_text'),
                   record.get('oracle_text'),
                   record.get('image_uris', {}).get('border_crop')) for record in batch]
        
        psycopg2.extras.execute_values(cursor, query, values)
        connection.commit()
        print(f'Upserted {i + batch_size} records.')

    print('Finished upserting records.')
    cursor.close()

def upsert_id_index_to_db(connection, id_index):
    cursor = connection.cursor()
    batch_size = 1000

    enumerated_id_index = list(enumerate(id_index))

    for i in range(0, len(enumerated_id_index), batch_size):
        batch = enumerated_id_index[i:i + batch_size]

        query = '''
            INSERT INTO id_index (scryfall_id, array_index)
            VALUES %s
            ON CONFLICT (scryfall_id) DO UPDATE
            SET array_index = EXCLUDED.array_index;
        '''
        
        values = [(scryfall_id, array_index) for array_index, scryfall_id in batch]

        psycopg2.extras.execute_values(cursor, query, values)
        print(f'Upserted {i + batch_size} id index records.')

    connection.commit()
    print('Finished upserting id index.')
    cursor.close()

def preprocess_data(data):
    data_dict = {'id': []}

    names = []
    oracle_texts = []
    keywords = []
    type_lines = []
    sets = []
    flavor_texts = []
    border_crop_urls = []

    processed_names = set()
    unique_data = []

    for record in data:
        if record.get('reprint', True):
            continue

        border_crop = record.get('image_uris', {}).get('border_crop', '')
        if not border_crop:
            continue

        name = record.get('name', '')
        if name in processed_names:
            continue
        processed_names.add(name)
        
        names.append(name)
        oracle_texts.append(record.get('oracle_text', ''))
        keywords.append(" ".join(record.get('keywords', [])))
        type_lines.append(record.get('type_line', ''))
        sets.append(record.get('set', ''))
        flavor_texts.append(record.get('flavor_text', ''))
        border_crop_urls.append(border_crop)

        unique_data.append(record)

        data_dict['id'].append(record.get('id', ''))

    return unique_data, data_dict, names, oracle_texts, type_lines, keywords

def train_model(data_dict, names, oracle_texts, type_lines, keywords):
    feature_df = pd.DataFrame(data_dict)

    vectorizer = CountVectorizer(max_features=5000)
    name_matrix = vectorizer.fit_transform(names)
    del vectorizer

    oracle_vectorizer = CountVectorizer(max_features=5000)
    oracle_matrix = oracle_vectorizer.fit_transform(oracle_texts)
    del oracle_vectorizer

    keyword_vectorizer = CountVectorizer(max_features=1000)
    keyword_matrix = keyword_vectorizer.fit_transform(keywords)
    del keyword_vectorizer

    type_vectorizer = CountVectorizer(max_features=30)
    type_matrix = type_vectorizer.fit_transform(type_lines)
    del type_vectorizer

    X = hstack([
        feature_df.drop('id', axis=1).values, 
        name_matrix,
        oracle_matrix,
        keyword_matrix,
        type_matrix
    ], format='csr')
    id_index = feature_df['id'].tolist()

    k = 30
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X, id_index)

    save_npz('../feature_matrix_compressed.npz', X)
    dump(knn, '../knn_model.joblib', compress=3)

    return id_index

if __name__ == '__main__':
    load_dotenv('.env.local')

    class Settings(BaseSettings):
        db_host: str = ""
        db_port: int = 5432
        db_name: str = ""
        db_user: str = ""
        db_password: str = ""

    settings = Settings()

    connection = connect_to_db(settings)

    if connection:
        with gzip.open('data.json.gz', 'rb') as f:
            content = f.read()
            content_str = content.decode('utf-8')
            data = json.loads(content_str)

        unique_data, data_dict, names, oracle_texts, type_lines, keywords = preprocess_data(data)

        id_index = train_model(data_dict, names, oracle_texts, type_lines, keywords)

        # only need to be run once when new base dataset is released from scryfall
        # upsert_data_to_db(connection, unique_data)
        # upsert_id_index_to_db(connection, id_index)

        connection.close()
    else:
        print('Connection failed.')