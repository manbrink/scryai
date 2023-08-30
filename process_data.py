import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Initialize dictionary to hold the data
data_dict = {'id': [], 'name': [], 'cmc': []}
for col in ['W', 'U', 'B', 'R', 'G']:
    data_dict[col] = []

# Set for keeping track of unique processed names
processed_names = set()

# Loop over each record in the JSON data
for record in data:
    # Get the name and skip this iteration if the name has already been processed
    name = record.get('name', '')
    if name in processed_names:
        continue

    # Mark this name as processed
    processed_names.add(name)

    # Append basic data
    data_dict['id'].append(record.get('id', ''))
    data_dict['cmc'].append(record.get('cmc', 0))
    data_dict['name'].append(record.get('name', ''))

    # Initialize colors to 0
    for col in ['W', 'U', 'B', 'R', 'G']:
        data_dict[col].append(0)

    # Update colors if present
    colors = record.get('colors', [])
    for col in colors:
        if col in ['W', 'U', 'B', 'R', 'G']:
            data_dict[col][-1] = 1

    # Add any new keywords found
    keywords = record.get('keywords', [])
    for keyword in keywords:
        if keyword not in data_dict:
            data_dict[keyword] = [0] * len(data_dict['id'])  # Initialize with zeros
        data_dict[keyword][-1] = 1  # Set the last element to 1

# Make sure all lists in data_dict have the same length
for key, value in data_dict.items():
    if len(value) < len(data_dict['id']):
        data_dict[key].extend([0] * (len(data_dict['id']) - len(value)))

# Convert the dictionary to a DataFrame
df_filtered = pd.DataFrame(data_dict)

# Initialize CountVectorizer
vectorizer = CountVectorizer(max_features=1000)

# Fit and transform the 'name' column
name_matrix = vectorizer.fit_transform(df_filtered['name'])

# Convert to array and add to DataFrame
name_array = name_matrix.toarray()

# Create new DataFrame with these arrays
df_name_vectorized = pd.DataFrame(name_array, columns=vectorizer.get_feature_names_out())

# Drop the original 'name' column from df_filtered
df_filtered.drop(['name'], axis=1, inplace=True)

# Concatenate the original DataFrame with the new 'name' vectorized DataFrame
df_final = pd.concat([df_filtered, df_name_vectorized], axis=1)

# Convert 'cmc' to integers and save DataFrame
df_final['cmc'] = df_final['cmc'].fillna(0).astype(int)
df_final.to_csv('processed_data_with_name.csv', index=False)

