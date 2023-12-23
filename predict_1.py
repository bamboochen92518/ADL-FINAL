from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from datasets import load_dataset
import torch
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_name",
    type=str,
    default="hw2942/chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1",
)
parser.add_argument(
    "--base_model",
    type=str,
    default="hw2942/chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1",
)
parser.add_argument(
    "--valid_data",
    type=str,
    default="valid.json",
)
args = parser.parse_args()

data_files = {}
data_files['train'] = "train_data/2301.TW.json"
args.datasets = load_dataset('json', data_files=data_files)

config = AutoConfig.from_pretrained(
    args.model_name,
    trust_remote_code=False,
    num_labels=2
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
    trust_remote_code=False,
    ignore_mismatched_sizes=True
)

data_num = 0
correct_predict = 0

json_data = []
with open(args.valid_data, 'r', encoding='utf8') as json_file:
    json_data = json.load(json_file)

for data in json_data:
    inputs = tokenizer(data["content"], return_tensors="pt", padding="max_length", max_length=2048, truncation=True)
    logits = model(**inputs).logits
    predicted_class_id = logits.argmax().item()
    predict_result = model.config.id2label[predicted_class_id]
    print(logits, predicted_class_id, predict_result, data['stock_result'])
    data_num += 1
    if predict_result == 'Up' and data['stock_result'] == 1:
        correct_predict += 1
    elif predict_result == 'Down' and data['stock_result'] == 0:
        correct_predict += 1
    elif predict_result == 'Down' and data['stock_result'] == -1:
        correct_predict += 1
    print(f'{correct_predict} / {data_num}')
