#!/bin/bash

epoch=20
learning_rates=(1e-5 2e-5 3e-5 4e-5 5e-5 1e-4 5e-6)
batch_sizes=(16 8 4 2 1)
accumulation_steps=(1 4)

for i in "${accumulation_steps[@]}"; do
  for j in "${batch_sizes[@]}"; do
    for k in "${learning_rates[@]}"; do
      nohup python train.py --model_name hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i > log/hw2942_bert-base-chinese-finetuning-financial-news-sentiment-test_${k}_${j}_${epoch}_${i}.log
      nohup python train.py --model_name bardsai/finance-sentiment-zh-base --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i > log/bardsai_finance-sentiment-zh-base_${k}_${j}_${epoch}_${i}.log
      nohup python train_1.py --model_name hw2942/chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1 --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i > log/hw2942_chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1_${k}_${j}_${epoch}_${i}.log
    done
  done
done

