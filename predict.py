from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from datasets import load_dataset
import torch
import argparse
import os
import json


def get_title(news: dict) -> str:
    return f'[{news["stock_code"]} {news["stock_name"]}] 新聞標題：{news["title"]}\n時間：{news["time"]}\n內文如下：\n'


def sliding_window(news: dict):
    # text = news["content"]
    title = f'[{news["stock_code"]} {news["stock_name"]}] 新聞標題：{news["title"]}\n時間：{news["time"]}\n內文如下：\n'
    text = title + news["content"]
    window_size = 512
    overlap = 0
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + window_size, len(text))
        # chunks.append([get_title(news) + text[start:end], end - start + 1])
        chunks.append([text[start:end], end - start + 1])
        start += window_size - overlap
    return chunks


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_name",
    type=str,
    default="bardsai/finance-sentiment-zh-base",
)
parser.add_argument(
    "--base_model",
    type=str,
    default="bardsai/finance-sentiment-zh-base",
)
args = parser.parse_args()

data_files = {}
data_files['train'] = "train_data/2301.TW.json"
args.datasets = load_dataset('json', data_files=data_files)

config = AutoConfig.from_pretrained(
    args.model_name,
    trust_remote_code=False,
    num_labels=3
)

tokenizer = AutoTokenizer.from_pretrained(
    args.base_model,
    use_fast=False,
    trust_remote_code=False,
    padding="max_length",
    truncation=True,
    paddind_side="left"
)

model = AutoModelForSequenceClassification.from_pretrained(
    args.model_name,
    from_tf=bool(".ckpt" in args.model_name),
    config=config,
    trust_remote_code=False
)

data_num = 0
correct_predict = 0

for file in os.listdir('train_data'):
    json_file_name = f'train_data/{file}'
    json_data = []
    with open(json_file_name, 'r', encoding='utf8') as json_file:
        json_data = json.load(json_file)

    for data in json_data:
        input_chunks = sliding_window(data)
        result = torch.tensor([[0.0, 0.0, 0.0]])
        for text in sliding_window(data):
            inputs = tokenizer(text[0], return_tensors="pt", padding="max_length", max_length=512, truncation=True)
            with torch.no_grad():
                logits = model(**inputs).logits
            result = torch.add(result, logits)
        predicted_class_id = result.argmax().item()
        predict_result = model.config.id2label[predicted_class_id]
        print(result, predict_result, data['stock_result'])
        data_num += 1
        if predict_result == 'positive' and data['stock_result'] == 1:
            correct_predict += 1
        elif predict_result == 'negative' and data['stock_result'] == -1:
            correct_predict += 1
        elif predict_result == 'neutral' and data['stock_result'] == 0:
            correct_predict += 1
        print(f'{correct_predict} / {data_num}')
