#!/bin/bash

epoch=10
learning_rates=(5e-06 1e-05 2e-05 3e-05)
batch_sizes=(4 2 1)
accumulation_steps=(1)

for i in "${accumulation_steps[@]}"; do
  for j in "${batch_sizes[@]}"; do
    for k in "${learning_rates[@]}"; do
      nohup python train.py --model_name hw2942/bert-base-chinese-finetuning-financial-news-sentiment-test --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i --max_seq_len 512 > log/hw2942_bert-base-chinese-finetuning-financial-news-sentiment-test_${k}_${j}_${epoch}_${i}.log
      nohup python train.py --model_name bert-base-chinese --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i --max_seq_len 512 > log/bardsai_finance-sentiment-zh-base_${k}_${j}_${epoch}_${i}.log
      nohup python train.py --model_name hw2942/chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1 --learning_rate $k --epoch $epoch --batch_size $j --accumulation_steps $i --max_seq_len 2048 > log/hw2942_chinese-bigbird-wwm-base-4096-wallstreetcn-morning-news-market-overview-open-000001SH-v1_${k}_${j}_${epoch}_${i}.log
    done
  done
done

