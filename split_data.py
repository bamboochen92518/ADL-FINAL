import json
import os


train_data = []
valid_data = []

for file in os.listdir('train_data'):
    json_file_name = f'train_data/{file}'
    json_data = []
    with open(json_file_name, 'r', encoding='utf8') as json_file:
        json_data = json.load(json_file)

    for data in json_data:
        if data["time"] >= "2023-11-01 00:00":
            valid_data.append(data)
        else:
            train_data.append(data)

with open('train.json', 'w', encoding='utf8') as json_file:
    json.dump(train_data, json_file, ensure_ascii=False, indent=5)

with open('valid.json', 'w', encoding='utf8') as json_file:
    json.dump(valid_data, json_file, ensure_ascii=False, indent=5)
