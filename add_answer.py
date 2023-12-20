import csv
import json
from datetime import datetime
from bisect import bisect_right


def convert_date(chinese_date):
    cleaned_date = chinese_date.replace('年', ' ').replace('月', ' ').replace('日', '')
    cleaned_date = cleaned_date.replace(' 下午', ' PM').replace(' 上午', ' AM')
    dt_obj = datetime.strptime(cleaned_date, "%Y %m %d %p%I:%M")
    formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M")
    return formatted_date


json_data = []
stock_set = set()

with open('train.json', 'r', encoding='utf8') as json_file:
    json_data = json.load(json_file)

for data in json_data:
    stock_code = data['stock_code']
    time = data['time']
    stock_set.add(stock_code)

stock_result = dict()
for stock_code in stock_set:
    file_name = f'stock_price/{stock_code}.csv'
    csv_data = []
    with open(file_name, 'r', newline='', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            csv_data.append(row)
    stock_result[stock_code] = dict()
    sz = len(csv_data)
    for idx in range(2, sz):
        time_stamp = f'{csv_data[idx][0]} 12:59'
        pre_result = csv_data[idx - 1][5]
        cur_result = csv_data[idx][5]
        if pre_result > cur_result:
            stock_result[stock_code][time_stamp] = -1
        else:
            stock_result[stock_code][time_stamp] = 1

new_json_data = []
for data in json_data:
    stock_code = data['stock_code']
    time = data['time']
    title = data['title']
    content = data['content']
    stock_name = data['stock_name']
    time_stamp = convert_date(time)
    sorted_keys = sorted(list(stock_result[stock_code].keys()))
    key_index = bisect_right(sorted_keys, time_stamp)
    if key_index == len(sorted_keys):
        continue
    next_close_time = sorted_keys[key_index]
    new_json_data.append({
        "title": title,
        "content": content,
        "time": time_stamp,
        "stock_name": stock_name,
        "stock_code": stock_code,
        "stock_result": stock_result[stock_code][next_close_time]
    })

with open('train_with_answer.json', 'w', encoding='utf8') as json_file:
    json.dump(new_json_data, json_file, ensure_ascii=False, indent=5)
