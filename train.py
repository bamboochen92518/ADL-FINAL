from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, Trainer, default_data_collator, TrainingArguments, get_scheduler
from datasets import load_dataset, load_metric
from torch.utils.data import DataLoader
import torch
import argparse
import numpy as np
# import os
# import json
# from tqdm import tqdm


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
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2",
)
parser.add_argument(
    "--learning_rate",
    type=float,
    default=1e-5,
)
parser.add_argument(
    "--epoch",
    type=int,
    default=1,
)
parser.add_argument(
    "--batch_size",
    type=int,
    default=1,
)
parser.add_argument(
    "--accumulation_steps",
    type=int,
    default=2,
)
parser.add_argument(
    "--train_data",
    type=str,
    default="train.json",
)
parser.add_argument(
    "--output_dir",
    type=str,
    default="new_model",
)
args = parser.parse_args()

device = torch.device("cuda")
data_files = {}
data_files['train'] = args.train_data
raw_datasets = load_dataset('json', data_files=data_files)

config = AutoConfig.from_pretrained(
    args.model_name,
    trust_remote_code=False,
    num_labels=3
)

tokenizer = AutoTokenizer.from_pretrained(
    args.model_name,
    use_fast=True,
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
)
model.to(device)

column_names = raw_datasets['train'].column_names


def preprocess_function(examples):
    inputs = [
        f'[{examples["time"][i]}] {examples["title"][i]}\n內文如下：\n{examples["content"][i]}'
        # examples["content"][i]
        for i in range(len(examples["content"]))
    ]
    result = tokenizer(inputs, padding="max_length", max_length=512, truncation=True)
    result["label"] = [1 - idx for idx in examples["stock_result"]]
    return result


raw_datasets = raw_datasets.map(
    preprocess_function,
    batched=True,
    remove_columns=column_names,
    load_from_cache_file=True,
)

train_dataset = raw_datasets['train']
train_dataset = train_dataset.rename_column("label", "labels")
train_dataset.set_format("torch")

train_dataloader = DataLoader(
    train_dataset,
    batch_size=args.batch_size
)

num_training_steps = args.epoch * len(train_dataloader)

optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate
)
lr_scheduler = get_scheduler(
    name='linear',
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

'''
progress_bar = tqdm(range(num_training_steps))
for epoch in range(args.epoch):
    model.train()
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

model.save_pretrained('new_model')
'''

train_argument = TrainingArguments(
    per_device_train_batch_size=args.batch_size,
    gradient_accumulation_steps=args.accumulation_steps,
    learning_rate=args.learning_rate,
    num_train_epochs=args.epoch,
    fp16=True,
    report_to='none',
    output_dir="new_model",
)

metric = load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


trainer = Trainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=None,
    tokenizer=tokenizer,
    data_collator=default_data_collator,
    args=train_argument,
    compute_metrics=compute_metrics,
    optimizers=[optimizer, lr_scheduler]
)

trainer.train()
model.save_pretrained(args.output_dir)
