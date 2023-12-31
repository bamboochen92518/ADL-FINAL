from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig, Trainer, default_data_collator, TrainingArguments, get_scheduler
from datasets import load_dataset, load_metric
from torch.utils.data import DataLoader
import torch
import argparse
import os
# import json
# from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_name",
    type=str,
    default="hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test",
)
parser.add_argument(
    "--learning_rate",
    type=float,
    default=1e-5,
)
parser.add_argument(
    "--epoch",
    type=int,
    default=10,
)
parser.add_argument(
    "--batch_size",
    type=int,
    default=1,
)
parser.add_argument(
    "--accumulation_steps",
    type=int,
    default=1,
)
parser.add_argument(
    "--train_data",
    type=str,
    default="train.json",
)
parser.add_argument(
    "--valid_data",
    type=str,
    default="valid.json",
)
parser.add_argument(
    "--output_dir",
    type=str,
    default=None,
)
parser.add_argument(
    "--max_seq_len",
    type=int,
    default=512,
)
args = parser.parse_args()

device = torch.device("cuda")
data_files = {}
data_files['train'] = args.train_data
data_files['valid'] = args.valid_data
raw_datasets = load_dataset('json', data_files=data_files)

num_labels = 2
if args.model_name == 'hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test':
    num_labels = 3

config = AutoConfig.from_pretrained(
    args.model_name,
    trust_remote_code=False,
    num_labels=num_labels,
    finetuning_task="text-classification",
)

tokenizer = AutoTokenizer.from_pretrained(
    args.model_name,
    use_fast=True,
    trust_remote_code=False,
    max_len=args.max_seq_len,
    padding="max_length",
    truncation=True,
    paddind_side="left"
)

model = AutoModelForSequenceClassification.from_pretrained(
    args.model_name,
    from_tf=bool(".ckpt" in args.model_name),
    config=config,
    trust_remote_code=False,
    ignore_mismatched_sizes=True,
)
model.to(device)

column_names = raw_datasets['train'].column_names


def preprocess_function(examples):
    inputs = [
        f'[{examples["time"][i]}] {examples["title"][i]}\n內文如下：\n{examples["content"][i]}'
        for i in range(len(examples["content"]))
    ]
    result = tokenizer(inputs, padding="max_length", max_length=args.max_seq_len, truncation=True)
    result["label"] = [idx for idx in examples["stock_result"]]
    if args.model_name == 'hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test':
        result["label"] = [idx * 2 for idx in examples["stock_result"]]
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
valid_dataset = raw_datasets['valid']
valid_dataset = valid_dataset.rename_column("label", "labels")
valid_dataset.set_format("torch")

train_dataloader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    shuffle=True
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

if args.output_dir is None:
    args.output_dir = f'{args.model_name}_{args.learning_rate}_{args.batch_size}_{args.epoch}_{args.accumulation_steps}'.replace('/', '_')

if not os.path.isdir(args.output_dir):
    os.mkdir(args.output_dir)

train_argument = TrainingArguments(
    per_device_train_batch_size=args.batch_size,
    gradient_accumulation_steps=args.accumulation_steps,
    learning_rate=args.learning_rate,
    num_train_epochs=args.epoch,
    fp16=True,
    report_to='all',
    output_dir=args.output_dir,
    per_device_eval_batch_size=1,
    save_strategy="epoch",
    save_steps=1,
    logging_strategy="epoch",
    logging_steps=1,
    logging_dir=f'{args.output_dir}/log',
    evaluation_strategy="epoch",
    eval_steps=1,
    # disable_tqdm=True,
)

metric = load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = []
    if args.model_name == 'hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test':
        for item in logits:
            if item[2] > item[0]:
                predictions.append(2)
            else:
                predictions.append(0)
    else:
        for item in logits:
            if item[1] > item[0]:
                predictions.append(1)
            else:
                predictions.append(0)

    result = metric.compute(predictions=predictions, references=labels)
    return result


trainer = Trainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    tokenizer=tokenizer,
    data_collator=default_data_collator,
    args=train_argument,
    compute_metrics=compute_metrics,
    optimizers=[optimizer, lr_scheduler],
)

trainer.train()
model.save_pretrained(args.output_dir)
