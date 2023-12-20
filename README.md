# ADL FINAL 透過財金新聞預測股價漲跌

#### `news.py`

爬新聞，將新聞存入`train.json`

#### `utils.py`

`get_stock_name_and_code(sectorID)`

透過`sectorID`抓取該類別的所有台股及其編號

`download_stock_price(stock_code)`

`stock_code`是一個list，下載list裡面的stock code所對應的歷史股價

檔案會存在`stock_price`這個資料夾裡面，如果檔案不存在會創建新的csv檔，檔案存在會append新的資料。

我們只看收盤價，所以拿`Adj Close`那欄的資料即可。

#### `train.json`

train data

#### `init.py`

每次跑之前都先執行`python init.py`，才會更新股價。

#### `add_answer.py`

將 train data 的資料加上 stock_result 那欄，如果是漲 / 持平就是 1，否則就是 -1。

另外將 time 的格式改為 `YYYY-MM-DD hour:minute`。

最終的結果存到 `train_with_answer.json`。
