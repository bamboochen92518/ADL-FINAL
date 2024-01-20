import utils
from datetime import datetime, timedelta
import json

print('請輸入你有興趣的股票類別')
utils.list_sectorID()
sectorID = int(input())

# 抓取類別名稱
target_stock_name, target_stock_code = utils.get_stock_name_and_code(sectorID)

# 選擇train or predict
print('請輸入模式')
print('1) train')
print('2) predict')
mode = int(input())
if mode != 1 and mode != 2:
    print('Invalid input')
    exit(0)

# 抓取新聞資料
print('請選擇新聞來源(輸入1, 2, or 3)')
print('1) yahoo')
print('2) 自由新聞網')
print('3) ET today')
news_source = int(input())

# 計算抓取新聞的日期
with open('setting.json', 'r') as json_file:
    data_dict = json.load(json_file)
input_date_str = data_dict['last_update']
input_date = datetime.strptime(input_date_str, '%Y%m%d')
tomorrow_date = input_date + timedelta(days=1)
today_datetime = datetime.today()
start_date = tomorrow_date.strftime('%Y%m%d')
end_date = today_datetime.strftime('%Y%m%d')

if news_source == 1:
    utils.get_news_from_yahoo(sectorID)
elif news_source == 2:
    utils.get_news_from_ltn(sectorID, start_date, end_date)
elif news_source == 3:
    utils.get_news_from_ettoday(sectorID)
else:
    print('Invalid input')
    exit(0)

# 更新setting.json
data_dict['last_update'] = end_date
with open('setting.json', 'w') as json_file:
    json.dump(data_dict, json_file, indent=4)

if mode == 1:
    # 下載歷史股票值
    utils.download_stock_price_csv(target_stock_code)

    # 加上股票 漲 / 跌 Label
    utils.add_label()

    # 將資料分為 train 及 validation
    utils.split_data_to_train_and_valid

exit(0)
