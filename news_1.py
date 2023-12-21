# https://search.ltn.com.tw/list?keyword=%E5%8F%B0%E7%A9%8D%E9%9B%BB&start_time=20041201&end_time=20231219&sort=date&type=business&page=1&fbclid=IwAR0FbdQnHhosAzmEZwe_GHVXLvMi8PQY23EThcIcLaeKxgZooY-0GdRzX1k
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from time import sleep
import argparse
from utils import get_stock_name_and_code

parser = argparse.ArgumentParser(description='')
parser.add_argument('--page_num', default=10)
parser.add_argument('--output_file', default='train.json')
parser.add_argument('--sectorID', default=41)

# 解析命令列參數
args = parser.parse_args()
# param
stock_name, stock_code = get_stock_name_and_code(args.sectorID)
start_time, end_time = '20041201', '20231219'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
seq_len = 1024
#請求網站
news_list = []
for i in range(len(stock_name)):
    name = stock_name[i]
    code = stock_code[i]
    print(f"正在抓取「{name}」的相關新聞")
    for page in range(args.page_num):
        url = 'https://search.ltn.com.tw/list?keyword=' + quote(name.encode('utf-8')) + '&start_time=' + start_time + '&end_time=' + end_time + '&sort=date&type=business&page=' + str(page + 1)
        print(url)
        try:
            list_req = requests.get(url, headers=headers)
        except:
            break
        if requests.status_codes != 200:
            break
        soup = BeautifulSoup(list_req.content, "html.parser")

        news_table = soup.find('ul', {'class': 'list boxTitle', 'data-desc': '列表'})
        news_body = news_table.find_all('li')

        for item in news_body:
            data = ['', '', '']
            cur_link = item.find('a')['href']
            cur_title = item.find('img')['title']
            # print(cur_link, cur_title)
            data[0] = str(cur_title)

            news_content = requests.get(cur_link)
            soup = BeautifulSoup(news_content.content, "html.parser")
            main_txt = soup.find('div', {'class': 'text'}).find_all('p')
            pub_time = soup.find('span', {'class': 'time'}).get_text()
            # print(main_txt)
            data[2] = str(pub_time)
            for subtext in main_txt:
                if subtext.find('img'):
                    continue
                text_body = subtext.get_text()
                if '點我訂閱' in str(text_body):
                    break
                else:
                    data[1] += str(text_body)
            news_list.append({'title': data[0], 'content': data[1], 'time': data[2], 'stock_name': name, 'stock_code': code})
            sleep(0.1)

    output_file = f"./stock_news/{code}_news.json"
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(news_list, json_file, indent=4, ensure_ascii=False)
    sleep(0.1)
