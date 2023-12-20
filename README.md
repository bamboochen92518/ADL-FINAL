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

