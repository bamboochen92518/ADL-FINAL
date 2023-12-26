import utils

print('輸入類別 (41: 電腦週邊, 46: 資訊服務, 40: 半導體, 38: 生技, 1: 水泥)')
sectorID = int(input())
target_stock_name, target_stock_code = utils.get_stock_name_and_code(sectorID)
# utils.get_news_from_yahoo(sectorID)
utils.get_news_from_ltn(sectorID, "20230101", "20231226")
# utils.get_news_from_ettoday(sectorID)
utils.download_stock_price_csv(target_stock_code)
