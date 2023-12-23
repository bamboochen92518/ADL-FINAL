from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from datasets import load_dataset
import torch
import argparse
import json


def sliding_window(news: dict):
    # text = news["content"]
    title = f'[{news["time"]}] {news["title"]}\n'
    # title = f'[{news["stock_code"]} {news["stock_name"]}] 新聞標題：{news["title"]}\n時間：{news["time"]}\n內文如下：\n'
    text = news["content"]
    window_size = 512 - len(title)
    overlap = 0
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + window_size, len(text))
        # chunks.append([get_title(news) + text[start:end], end - start + 1])
        chunks.append([title + text[start:end], end - start + 1])
        start += window_size - overlap
    return chunks


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_name",
    type=str,
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2",
)
parser.add_argument(
    "--base_model",
    type=str,
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2",
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

json_data = []
with open(args.valid_data, 'r', encoding='utf8') as json_file:
    json_data = json.load(json_file)

for data in json_data:
    input_chunks = sliding_window(data)
    result = torch.tensor([[0.0, 0.0, 0.0]])
    for text in sliding_window(data):
        inputs = tokenizer(text[0], return_tensors="pt", padding="max_length", max_length=512, truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        result = torch.add(result, logits * text[1] / 512)
    predicted_class_id = result.argmax().item()
    predict_result = model.config.id2label[predicted_class_id]
    print(result, predict_result, data['stock_result'])
    data_num += 1
    if predict_result == 'Positive' and data['stock_result'] == 1:
        correct_predict += 1
    elif predict_result == 'Negative' and data['stock_result'] == -1:
        correct_predict += 1
    elif predict_result == 'Neutral' and data['stock_result'] == 0:
        correct_predict += 1
    print(f'{correct_predict} / {data_num}')
