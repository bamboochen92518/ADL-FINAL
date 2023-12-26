# ADL FINAL 透過財金新聞預測股價漲跌

### How to run

```bash
$ python init.py
$ python train.py --model_name {model_name}\
                  --learning_rate {learning_rate}\
                  --epoch {epoch}\
                  --batch_size {batch_size}\
                  --accumulation_steps {accumulation_steps}\
                  --train_data {train_data}\
                  --valid_data {valid_data}\
                  --output_dir {output_dir}\
                  --max_seq_len {max_seq_len}
$ python predict.py --model_name {model_name}\
                    --base_model {base_model}\
                    --valid_data {valid_data}\
                    --max_seq_len {max_seq_len}
```

### File

#### `init.py`

Initialize or update stock price and financial news that you interested. 

#### `utils.py`

`get_stock_name_and_code(sectorID)`

Get all the stock name and code with `sectorID`. 

`download_stock_price_csv(stock_code)`

Download history stock price with stock code in the list. 

`get_news_from_yahoo(sectorID)`

Download financial news from yahoo news with `sectorID`. 

`get_news_from_ltn(sectorID)`

Download financial news from Liberty  News with `sectorID`. 

`get_news_from_ettoday(sectorID)`

Download financial news from ettoday with `sectorID`. 

#### `train.json`

Train data

#### `valid.json`

Validation data

#### `train.py`

Train model, the arguments are shown in `How to run`. 

#### `predict.py`

Predict result, the arguments are shown in `How to run`. 

### directory

#### stock_news

There are many `{stock code}_news.json` in it, which includes the news of that company or stock. 

#### stock_price

There are many `{stock code}.csv` in it, which includes the stock price of that company or stock. 

#### stock_data

There are many `{stock code}.json` in it, which includes the news and label of that company or stock. 
