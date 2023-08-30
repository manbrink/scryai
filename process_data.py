import json
import pandas as pd

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare an empty dictionary for holding data
data_dict = {'id': [], 'cmc': []}
for col in ['W', 'U', 'B', 'R', 'G']:
    data_dict[col] = []

# Set of all unique keywords across all records
all_keywords = set()

# Iterate over records to populate color and keyword columns
for record in data:
    data_dict['id'].append(record.get('id', ''))
    data_dict['cmc'].append(record.get('cmc', 0))

    # Initialize colors to 0
    for col in ['W', 'U', 'B', 'R', 'G']:
        data_dict[col].append(0)

    colors = record.get('colors', [])
    if isinstance(colors, list):
        for col in colors:
            if col in ['W', 'U', 'B', 'R', 'G']:
                data_dict[col][-1] = 1  # set the last entry to 1
    
    # Update the set of all unique keywords
    keywords = record.get('keywords', [])
    if isinstance(keywords, list):
        all_keywords.update(keywords)

# Add keyword columns to dictionary and initialize them to 0
for keyword in all_keywords:
    data_dict[keyword] = [0] * len(data)

# Iterate again to populate keyword columns
for i, record in enumerate(data):
    keywords = record.get('keywords', [])
    if isinstance(keywords, list):
        for keyword in keywords:
            if keyword in all_keywords:
                data_dict[keyword][i] = 1

# Convert the dictionary to a DataFrame
df_filtered = pd.DataFrame(data_dict)

# Convert 'cmc' to integers
df_filtered['cmc'] = df_filtered['cmc'].fillna(0).astype(int)

df_filtered.to_csv('processed_data.csv', index=False)

# Show the first 10 rows
# print(df_filtered.head(10))


