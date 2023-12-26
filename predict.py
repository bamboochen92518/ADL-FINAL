from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import torch
import argparse
import json


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_name",
    type=str,
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test",
)
parser.add_argument(
    "--base_model",
    type=str,
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test",
)
parser.add_argument(
    "--valid_data",
    type=str,
    default="valid.json",
)
parser.add_argument(
    "--max_seq_len",
    type=int,
    default=512,
)
args = parser.parse_args()


def sliding_window(news: dict):
    title = f'[{news["time"]}] {news["title"]}\n'
    text = news["content"]
    window_size = args.max_seq_len - len(title)
    overlap = window_size - window_size // 4
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + window_size, len(text))
        chunks.append([title + text[start:end], end - start + 1])
        start += window_size - overlap
    return chunks


label_num = 2
if args.base_model == "hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test":
    label_num = 3

config = AutoConfig.from_pretrained(
    args.model_name,
    trust_remote_code=False,
    num_labels=label_num
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
    data_num += 1
    if args.base_model == "hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test":
        input_chunks = sliding_window(data)
        result = torch.tensor([[0.0, 0.0, 0.0]])
        for text in sliding_window(data):
            inputs = tokenizer(text[0], return_tensors="pt", padding="max_length", max_length=args.max_seq_len, truncation=True)
            with torch.no_grad():
                logits = model(**inputs).logits
            result = torch.add(result, logits * text[1])
        predicted_class_id = result.argmax().item()
        if result[0][2] > result[0][0]:
            predicted_class_id = 2
        else:
            predicted_class_id = 0
        predict_result = model.config.id2label[predicted_class_id]
        print(result, predict_result, data['stock_result'])
        if predict_result == 'Positive' and data['stock_result'] == 1:
            correct_predict += 1
        elif predict_result == 'Negative' and data['stock_result'] == 0:
            correct_predict += 1
        print(f'{correct_predict} / {data_num}')

    elif args.base_model == "hw2942/chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1":
        inputs = tokenizer(data["content"], return_tensors="pt", padding="max_length", max_length=args.max_seq_len, truncation=True)
        logits = model(**inputs).logits
        predicted_class_id = logits.argmax().item()
        predict_result = model.config.id2label[predicted_class_id]
        print(logits, predicted_class_id, predict_result, data['stock_result'])
        if predict_result == 'Up' and data['stock_result'] == 1:
            correct_predict += 1
        elif predict_result == 'Down' and data['stock_result'] == 0:
            correct_predict += 1
        print(f'{correct_predict} / {data_num}')

    else:
        input_chunks = sliding_window(data)
        result = torch.tensor([[0.0, 0.0]])
        for text in sliding_window(data):
            inputs = tokenizer(text[0], return_tensors="pt", padding="max_length", max_length=args.max_seq_len, truncation=True)
            with torch.no_grad():
                logits = model(**inputs).logits
            result = torch.add(result, logits * text[1])
        predicted_class_id = result.argmax().item()
        if result[0][1] > result[0][0]:
            predicted_class_id = 1
        else:
            predicted_class_id = 0
        predict_result = model.config.id2label[predicted_class_id]
        print(result, predict_result, data['stock_result'])
        if predict_result == 'LABEL_1' and data['stock_result'] == 1:
            correct_predict += 1
        elif predict_result == 'LABEL_0' and data['stock_result'] == 0:
            correct_predict += 1
        print(f'{correct_predict} / {data_num}')
