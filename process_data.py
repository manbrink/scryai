import json
import pandas as pd

# Load JSON data
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Initialize dictionary to hold the data
data_dict = {'id': [], 'cmc': []}
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

# Convert to DataFrame
df_filtered = pd.DataFrame(data_dict)

# Clean up the 'cmc' column
df_filtered['cmc'] = df_filtered['cmc'].fillna(0).astype(int)

# Write to CSV
df_filtered.to_csv('processed_data.csv', index=False)
