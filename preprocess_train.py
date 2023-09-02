import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import KNeighborsClassifier
from joblib import dump

import psycopg2
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

    for i in range(0, len(unique_data), batch_size):
        batch = unique_data[i:i + batch_size]
        query = '''
            INSERT INTO scryfall (scryfall_id, name, type_line, set, flavor_text, oracle_text, border_crop_url)
            VALUES %s
            ON CONFLICT (scryfall_id) DO UPDATE
            SET name = EXCLUDED.name,
                type_line = EXCLUDED.type_line,
                set = EXCLUDED.set,
                flavor_text = EXCLUDED.flavor_text,
                oracle_text = EXCLUDED.oracle_text,
                image_uris_border_crop = EXCLUDED.image_uris_border_crop;
        '''
        values = [(record.get('id'), 
                   record.get('name'),
                   record.get('type_line'),
                   record.get('set'),
                   record.get('flavor_text'),
                   record.get('oracle_text'),
                   record.get('image_uris', {}).get('border_crop')) for record in batch]
        
        cursor.execute(query, values)
        connection.commit()
        
    cursor.close()

def upsert_id_index_to_db(connection, id_index):
    cursor = connection.cursor()

    for array_index, scryfall_id in enumerate(id_index):
        query = '''
            INSERT INTO id_index_table (scryfall_id, array_index)
            VALUES (%s, %s)
            ON CONFLICT (scryfall_id) DO UPDATE
            SET array_index = EXCLUDED.array_index;
        '''
        cursor.execute(query, (scryfall_id, array_index))

    connection.commit()
    cursor.close()

def preprocess_data(data):
    data_dict = {'id': [], 'cmc': []}
    for col in ['W', 'U', 'B', 'R', 'G']:
        data_dict[col] = []

    names = []
    oracle_texts = []
    type_lines = []
    sets = []
    flavor_texts = []
    border_crop_urls = []

    all_keywords = set()
    processed_names = set()
    unique_data = []

    for record in data:
        name = record.get('name', '')
        if name in processed_names:
            continue
        processed_names.add(name)
        
        names.append(name)
        oracle_texts.append(record.get('oracle_text', ''))
        type_lines.append(record.get('type_line', ''))
        sets.append(record.get('set', ''))
        flavor_texts.append(record.get('flavor_text', ''))
        border_crop_urls.append(record.get('image_uris', {}).get('border_crop', ''))

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

    return unique_data, data_dict, names, oracle_texts, type_lines, sets, flavor_texts

def train_model(data_dict, names, oracle_texts, type_lines, sets, flavor_texts):
    df_filtered = pd.DataFrame(data_dict)

    vectorizer = CountVectorizer(max_features=3000)
    name_matrix = vectorizer.fit_transform(names)
    name_array = name_matrix.toarray()

    oracle_vectorizer = CountVectorizer(max_features=3000)
    oracle_matrix = oracle_vectorizer.fit_transform(oracle_texts)
    oracle_array = oracle_matrix.toarray()

    type_vectorizer = CountVectorizer(max_features=500)
    type_matrix = type_vectorizer.fit_transform(type_lines)
    type_array = type_matrix.toarray()

    set_vectorizer = CountVectorizer(max_features=1000)
    set_matrix = set_vectorizer.fit_transform(sets)
    set_array = set_matrix.toarray()

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

    k = 30
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X, id_index)

    np.save('feature_matrix.npy', X)

    dump(knn, 'knn_model.joblib')

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

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    unique_data, data_dict, names, oracle_texts, type_lines, sets, flavor_texts = preprocess_data(data)

    id_index = train_model(data_dict, names, oracle_texts, type_lines, sets, flavor_texts)

    if connection:
        upsert_data_to_db(connection, unique_data)
        upsert_id_index_to_db(connection, id_index)
        connection.close()